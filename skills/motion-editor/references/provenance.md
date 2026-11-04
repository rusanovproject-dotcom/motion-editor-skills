# Откуда взяты решения

Дата фактуры: 4 ноября 2026. Назначение: переиспользуемые анимации и графические вставки в разговорные видео. Ниже отделены наблюдения визуальных приёмов от проектных решений. Наблюдения и переносимые решения различаются:

| Источник | Наблюдение / статус | Что меняет в skill |
|---|---|---|
| Пример Bubble Wrap | observed: светлый editorial, blue accent, объект превращается в переход | clean-editorial, semantic transformations, проверка точного момента смены |
| Пример Webcam | observed: бумажные предметные вырезки, повторяющийся предмет, сетка и camera-like zoom | paper-collage, object continuity, group animation |
| Пример Tamagotchi | observed: отдельно корпус/экран, пиксельные состояния, рекламные наклейки, ретро-overlay | retro-vhs, nested local screen, независимые состояния |
| Назначение пакета | derived: повторное производство требует редактируемых сцен | executable sources + render, не только план |
| Наше проектирование | derived: одинаковые исходники и кадры сравнения позволяют отделить fidelity от похожей палитры | short moving pilot, asset substitutions, сравнительная проверка |
| Контекст новой речи | derived: неизвестные слова/время нельзя синхронизировать достоверно | provisional anchors, полезный прототип без выдуманного монтажа |

Оригинальные MP4, фото людей и транскрипты не скопированы в runtime-пакет. Стилевые описания — дистилляция приёмов. Kit содержит оригинальные синтетические демонстрации, не исходные предметные ассеты. Наличие kit не означает, что достигнуто «1 в 1».

Официальная документация, проверенная в исследовании: [Remotion skills](https://www.remotion.dev/docs/ai/skills), [анимация](https://www.remotion.dev/docs/animating-properties), [HyperFrames determinism](https://github.com/heygen-com/hyperframes/blob/main/docs/concepts/determinism.mdx), [reverse workflow](https://github.com/heygen-com/hyperframes/blob/main/skills/reverse-any-video/SKILL.md). Это технические источники, не гарантия визуального качества и не разрешение выполнять платные/облачные действия.

Источники практики: [Joseph](https://www.youtube.com/watch?v=5UnK3c-nlIs) — план фраз/сцен, визуальный и звуковой гайды; [Nate Herk](https://www.youtube.com/watch?v=7jHXoPGnA4c) — reusable style rules; [Duncan Rogoff](https://www.youtube.com/watch?v=Wkf2IjZrRt4) — reference analysis и статичные ключевые кадры до движения. Они подкрепляют метод планирования и итераций; конкретные параметры starter kit созданы нами.

При новом референсе сохраняй наблюдаемое и измеренное отдельно от решения о реализации. При неизвестных ассетах, шрифтах, скрытых областях или аудио не заполняй пробел уверенностью.

Точечное усиление: derived из прежнего исследования Duncan Rogoff (композиция до движения), MoSidd (поэтапный reveal и движение группы), сообщества onetake (непрерывность без переноса его кода) и разделения результата на два режима. Добавлены короткая партитура и выбор исходного материала. Это наши решения, не дословные советы авторов. Технические источники повторно проверены 4 ноября 2026: [Lottie](https://www.remotion.dev/docs/lottie), [поиск Lottie](https://www.remotion.dev/docs/lottie/lottiefiles), [paths](https://www.remotion.dev/docs/paths), [templates](https://www.remotion.dev/templates/), [React Bits](https://github.com/DavidHDev/react-bits). Пакеты из каталога не устанавливались и не считаются протестированными в локальном engine.
