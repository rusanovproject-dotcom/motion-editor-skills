import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parent.parent/'skills/motion-editor'

def load(name,root=ROOT):
    spec=importlib.util.spec_from_file_location('module_'+name,root/'scripts'/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

class ModuleTests(unittest.TestCase):
    def test_alias_priority_ambiguity_and_unknown(self):
        m=load('style_registry');styles=m.load_registry(ROOT)
        self.assertEqual(set(styles),{'clean-editorial','paper-collage','retro-vhs'})
        for alias,ident in [('R4','clean-editorial'),('Webcam','paper-collage'),('R12-tamagotchi.mp4','retro-vhs')]:
            self.assertEqual(m.resolve_style(styles,explicit=alias)['style_id'],ident)
        self.assertEqual(m.resolve_style(styles,explicit='R4',references=['R2-webcam.mp4'],query='VHS')['style_id'],'clean-editorial')
        self.assertEqual(m.resolve_style(styles,references=['R2-webcam.mp4'])['style_id'],'paper-collage')
        self.assertEqual(m.resolve_style(styles,query='бумажный коллаж')['style_id'],'paper-collage')
        self.assertEqual(m.resolve_style(styles,query='clean-editorial и retro-vhs')['status'],'ambiguous')
        self.assertEqual(m.resolve_style(styles,explicit='unknown-style')['status'],'unknown_style')
        self.assertEqual(m.resolve_style(styles,query='просто обрежь две секунды')['status'],'needs_style')

    def test_duplicate_alias_and_escaping_renderer_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/'skill';shutil.copytree(ROOT,root)
            m=load('style_registry',root);manifest=root/'styles/paper-collage/style.json';original=json.loads(manifest.read_text())
            d=copy.deepcopy(original);d['aliases'].append('R4');manifest.write_text(json.dumps(d))
            with self.assertRaisesRegex(ValueError,'Alias collision'):m.load_registry(root)
            d=copy.deepcopy(original);d['renderer']='../../assets/scene-kit/SceneKit.tsx';manifest.write_text(json.dumps(d))
            with self.assertRaisesRegex(ValueError,'escaping'):m.load_registry(root)

    def test_fourth_style_needs_no_core_change_and_scaffolds(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);root=base/'skill';shutil.copytree(ROOT,root)
            core=[root/'SKILL.md',*list((root/'scripts').glob('*.py')),*list((root/'assets/scene-kit').glob('*.tsx'))]
            before={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in core}
            folder=root/'styles/extension-probe';shutil.copytree(root/'styles/clean-editorial',folder)
            manifest=json.loads((folder/'style.json').read_text());manifest.update(id='extension-probe',name='Extension test',aliases=['Probe Four'],keywords=['test-plugin-only']);(folder/'style.json').write_text(json.dumps(manifest))
            registry=root/'styles/registry.json';d=json.loads(registry.read_text());d['styles'].append('extension-probe/style.json');registry.write_text(json.dumps(d))
            module=load('style_registry',root);styles=module.load_registry(root)
            self.assertEqual(len(styles),4)
            self.assertEqual(module.resolve_style(styles,explicit='Probe Four')['style_id'],'extension-probe')
            engine=base/'engine';(engine/'node_modules/.bin').mkdir(parents=True);(engine/'node_modules/remotion').mkdir();(engine/'node_modules/remotion/package.json').write_text('{}');(engine/'node_modules/.bin/remotion').write_text('#!/bin/sh\nexit 99\n')
            result=load('scaffold_scene',root).scaffold(base/'project',engine,'extension-probe',320,560,30,1)
            self.assertEqual(json.loads((base/'project/scene.json').read_text())['style'],'extension-probe')
            self.assertTrue((base/'project/styles/extension-probe/Scene.tsx').is_file())
            self.assertIn('extension-probe',(base/'project/SceneKit.tsx').read_text())
            self.assertEqual(before,{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in core})
            # Entry remains backward-compatible: every registered style can be selected in scene.json.
            self.assertIn('paper-collage',(base/'project/SceneKit.tsx').read_text())

    def test_invalid_defaults_rejected_and_panel_only_style_scaffolds(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);root=base/'skill';shutil.copytree(ROOT,root)
            manifest=root/'styles/clean-editorial/style.json';original=json.loads(manifest.read_text())
            d=copy.deepcopy(original);d['defaults']['labels']='abc';manifest.write_text(json.dumps(d))
            with self.assertRaisesRegex(ValueError,'defaults.labels'):load('style_registry',root).load_registry(root)
            d=copy.deepcopy(original);d['capabilities']=['unsupported-layout'];manifest.write_text(json.dumps(d))
            with self.assertRaisesRegex(ValueError,'supported layouts'):load('style_registry',root).load_registry(root)
            d=copy.deepcopy(original);d['capabilities']=['lower-panel'];manifest.write_text(json.dumps(d))
            engine=base/'engine';(engine/'node_modules/.bin').mkdir(parents=True);(engine/'node_modules/remotion').mkdir();(engine/'node_modules/remotion/package.json').write_text('{}');(engine/'node_modules/.bin/remotion').write_text('#!/bin/sh\nexit 99\n')
            load('scaffold_scene',root).scaffold(base/'project',engine,'clean-editorial',320,560,30,1)
            self.assertEqual(json.loads((base/'project/scene.json').read_text())['layout'],'lower-panel')
            d['defaults']['layout']='fullscreen';manifest.write_text(json.dumps(d))
            with self.assertRaisesRegex(ValueError,'defaults.layout'):load('style_registry',root).load_registry(root)

if __name__=='__main__':unittest.main(verbosity=2)
