# Приёмка и локальное добавление

Рабочий каталог доказательств держи рядом со skill workspace, отдельно от runtime. Сначала сделай копию editor в staging и сохрани SHA256 исходного `styles/registry.json`. Сохраняй существующие стили и все их files. Прочитай актуальные flags `scaffold_scene.py --help`; scaffold использует реестр той копии, из которой он запущен.

Для каждого заявленного layout отрендери две короткие темы: исходную и перенос на иной предмет/смысл с другими текстами. Для lower-panel положи локальный фон в `project/public`, задай `backgroundVideo` относительным именем и `layout: lower-panel` в scene.json. Без фонового видео можно дополнительно сделать alpha-layer, но это не заменяет композитный preview. Родитель владеет размещением, речь/EDL не переписывается стилем.

QA: реестр/ID/alias проходят; старые IDs на месте; видео действительно декодируется, размеры/FPS/duration верны; нет скачков на seek; предметное действие читается; нет обрезаний/пропавшего текста на переходе; compact виден на телефоне; верхняя зона композита сохранена. Отдельно проверь unique SVG IDs при нескольких экземплярах. Для ассетов и шрифтов укажи точные и заменённые.

После просмотра сформируй QA receipt вне runtime:

```json
{
  "module_sha256": "tree_hash готовой папки модуля",
  "reviewed": true,
  "renders": [
    {"layout":"fullscreen", "topic":"тема A", "path":"/absolute/render-a.mp4", "sha256":"file hash"},
    {"layout":"fullscreen", "topic":"тема B", "path":"/absolute/render-b.mp4", "sha256":"file hash"},
    {"layout":"lower-panel", "topic":"тема A", "path":"/absolute/overlay-a.mp4", "sha256":"file hash"},
    {"layout":"lower-panel", "topic":"тема B", "path":"/absolute/overlay-b.mp4", "sha256":"file hash"}
  ]
}
```

`module_sha256` вычисляется `tree_hash` из `scripts/register_style.py`; file hashes — SHA256 bytes. Параметр reviewed — запись выполненного визуального просмотра, а не автоматическая оценка качества. Helper проверяет hash, ffprobe и две темы на capability; он не определяет соответствие эстетике и не доказывает, что видео сделано именно этим кодом. Сохраняй команды/scaffold projects и исходные файлы как трассу.

Подключение из каталога конструктора:

```sh
python3 scripts/register_style.py --editor /path/to/motion-editor --module /path/to/staged/module --registry-sha SHA256_OF_REGISTRY --qa /path/to/qa.json
```

Helper использует advisory lock, compare-before-write и атомарную замену реестра; все параллельные авторы должны использовать этот helper/тот же lock. Произвольный внешний процесс, игнорирующий lock, не защищён от гонки между последней проверкой и rename. Не выполняй ручные concurrent edits registry. При stale hash перечитай актуальный реестр, повтори проверку коллизий и валидацию объединения, затем обнови ожидаемый hash. Существующий ID/папка не перезаписывается; upgrade существующего стиля — отдельный workflow со snapshot.

После подключения снова проверь live registry и один scaffold. Ранее созданные output projects не обновляются сами. Если требуется откат уже добавленного модуля: под тем же lock проверь, что его hash совпал с твоим, удали только его запись из **текущего** реестра атомарной заменой, затем перенеси только его папку в workspace. При чужом изменении модуля останови откат. Не восстанавливай полный старый registry — так теряются чужие стили.
