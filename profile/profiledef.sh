#!/usr/bin/env bash
# AetherOS archiso profile definition
# shellcheck disable=SC2034

iso_name="aetheros"
iso_label="AETHEROS_$(date +%Y%m)"
iso_publisher="AetherOS Project <https://example.invalid>"
iso_application="AetherOS Live/Install medium"
iso_version="$(date +%Y.%m.%d)"
install_dir="aetheros"
buildmodes=('iso')
bootmodes=(
    'bios.syslinux.mbr'
    'bios.syslinux.eltorito'
    'uefi-x64.grub.esp'
    'uefi-x64.grub.eltorito'
)
arch="x86_64"
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'zstd' '-Xcompression-level' '19')
bootstrap_tarball_compression=('zstd' '-c' '-T0' '--long' '-19')
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/root"]="0:0:750"
  ["/root/.automated_script.sh"]="0:0:755"
  ["/usr/local/bin/aether"]="0:0:755"
  ["/usr/local/bin/aether-info"]="0:0:755"
  ["/usr/local/bin/aether-version"]="0:0:755"
  ["/usr/local/bin/aether-about"]="0:0:755"
  ["/usr/local/bin/aether-update"]="0:0:755"
  ["/usr/local/bin/aether-repair"]="0:0:755"
  ["/usr/local/bin/aether-clean"]="0:0:755"
  ["/usr/local/bin/aether-check"]="0:0:755"
  ["/usr/local/bin/aether-report"]="0:0:755"
  ["/usr/local/bin/network-info"]="0:0:755"
  ["/usr/local/bin/wifi-info"]="0:0:755"
  ["/usr/local/bin/ip-info"]="0:0:755"
  ["/usr/local/bin/aether-store"]="0:0:755"
  ["/usr/local/bin/aether-theme"]="0:0:755"
  ["/usr/local/bin/aether-sound-test"]="0:0:755"
  ["/usr/local/bin/aether-rain"]="0:0:755"
  ["/usr/local/bin/aether-wave"]="0:0:755"
  ["/usr/local/bin/aether-cycle"]="0:0:755"
  ["/usr/local/bin/aether-journal"]="0:0:755"
  ["/usr/local/bin/aether-welcome"]="0:0:755"
  ["/usr/local/bin/aether-about-gui"]="0:0:755"
  ["/etc/skel/Desktop/Начало работы.desktop"]="0:0:755"
  ["/etc/skel/Desktop/Aether Store.desktop"]="0:0:755"
  ["/etc/skel/Desktop/Aether Info.desktop"]="0:0:755"
  ["/root/customize_airootfs.sh"]="0:0:755"
  ["/etc/skel/Desktop/Install AetherOS.desktop"]="0:0:755"
)
