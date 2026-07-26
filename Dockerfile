# AetherOS build container — lets you build the ISO from any host
# (Linux/macOS/Windows with Docker) without installing Arch Linux yourself.
FROM archlinux:latest

RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm --needed archiso git base-devel grub syslinux dosfstools mtools && \
    pacman-key --recv-key 3056513887B78AEB --keyserver keyserver.ubuntu.com && \
    pacman-key --lsign-key 3056513887B78AEB && \
    pacman -U --noconfirm \
        'https://cdn-mirror.chaotic.cx/chaotic-aur/chaotic-keyring.pkg.tar.zst' \
        'https://cdn-mirror.chaotic.cx/chaotic-aur/chaotic-mirrorlist.pkg.tar.zst' && \
    pacman -Scc --noconfirm

WORKDIR /aetheros
ENTRYPOINT ["/bin/bash", "/aetheros/build.sh"]
