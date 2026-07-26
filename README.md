# AetherOS

Собственный дистрибутив на базе **Arch Linux**, объединяющий гибкость Arch,
простоту установки Ubuntu и удобство рабочего стола Linux Mint — под
собственным брендом AetherOS.

Полное пошаговое руководство: [`docs/GUIDE.md`](docs/GUIDE.md) (на русском).

## Быстрый старт

Если у вас Arch Linux:
```bash
sudo ./build.sh
```

Если у вас Windows / macOS / Ubuntu (через Docker):
```bash
./docker-build.sh
```

Через 15–40 минут в корне проекта появится `AetherOS.iso`.

## Что внутри

| Компонент | Технология | Где искать |
|---|---|---|
| База системы | Arch Linux (rolling) | `profile/packages.x86_64` |
| Рабочий стол | Aether Desktop (XFCE) | `profile/airootfs/etc/skel/.config/xfce4/` |
| Терминал | Aether Terminal (xfce4-terminal, свой стиль) | `.../xfce4/terminal/terminalrc` |
| Команды | `aether`, `aether-info`, `aether-store`, ... | `profile/airootfs/usr/local/bin/` |
| Установщик | Aether Installer (Calamares) | `profile/airootfs/etc/calamares/` |
| Загрузка | GRUB + Plymouth, тема AetherOS | `profile/airootfs/boot/grub/themes/`, `.../plymouth/themes/` |
| Обои / логотип | сгенерированы программно (Pillow) | `branding/generate_assets.py` |
| Автосборка ISO | archiso (`mkarchiso`) | `build.sh`, `docker-build.sh` |
| Тесты | загрузка в headless QEMU | `tests/smoke-test.sh` |

## Структура проекта

```
AetherOS/
├── build.sh              # сборка ISO (на Arch Linux)
├── docker-build.sh        # сборка ISO через Docker (любая ОС)
├── Dockerfile
├── profile/               # archiso-профиль дистрибутива
│   ├── profiledef.sh
│   ├── pacman.conf
│   ├── packages.x86_64
│   └── airootfs/          # файлы, которые попадут в готовую систему "как есть"
├── branding/               # генератор обоев/логотипа
├── docs/                  # документация
└── tests/                 # автоматическая проверка сборки
```

## Важно

Сборка ISO требует Arch Linux (`archiso`/`mkarchiso`) и доступа в интернет
(скачиваются реальные пакеты Arch). Это нельзя запустить в оффлайн-песочнице —
запускайте `build.sh`/`docker-build.sh` на своей машине.
