#!/usr/bin/env bash
# Executed once, inside the airootfs chroot, by mkarchiso during the ISO build.
# archiso removes this file automatically afterwards.
set -e -u

echo "==> AetherOS: customizing airootfs..."

# --- hostname ---
echo "aetheros" > /etc/hostname

# --- locales ---
locale-gen

# --- timezone (sensible default; the installer lets the real user pick their own) ---
ln -sf /usr/share/zoneinfo/UTC /etc/localtime

# --- make sure our scripts are executable regardless of how they were copied in ---
chmod 755 /usr/local/bin/aether* /usr/local/bin/network-info /usr/local/bin/wifi-info /usr/local/bin/ip-info

# --- default live session user (branded "aether"), used only on the live/boot medium ---
if ! id -u admin >/dev/null 2>&1; then
    useradd -m -G wheel,audio,video,storage,optical,network,power -s /bin/bash admin
    cp -f /etc/skel/.face /home/admin/.face 2>/dev/null || true
    chown admin:admin /home/admin/.face 2>/dev/null || true
    echo "admin:admin" | chpasswd
fi

# --- root has no usable password on the live medium (login is via the live user) ---
passwd -l root || true

# --- AUR helper (yay) — gives 'aether install' access to the AUR too,
#     and lets users freely customize/rebuild the system like on Arch ---
if ! command -v yay >/dev/null 2>&1 && command -v makepkg >/dev/null 2>&1; then
    tmp_build_user="_aetherbuild"
    useradd -m -s /bin/bash "${tmp_build_user}" || true
    echo "${tmp_build_user} ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/90-aether-build
    su - "${tmp_build_user}" -c '
        set -e
        cd /tmp
        git clone --depth=1 https://aur.archlinux.org/yay-bin.git
        cd yay-bin
        makepkg -si --noconfirm
    ' || echo "WARN: yay build failed (no network during build?) — 'aether install' will still work via pacman."
    rm -f /etc/sudoers.d/90-aether-build
    userdel -r "${tmp_build_user}" 2>/dev/null || true
fi

# --- AetherOS sound theme: register as the default via dconf ---
mkdir -p /etc/dconf/profile /etc/dconf/db/local.d
cat > /etc/dconf/profile/user <<'EOF'
user-db:user
system-db:local
EOF
cat > /etc/dconf/db/local.d/00-aetheros-sound <<'EOF'
[org/gnome/desktop/sound]
theme-name='aetheros'
event-sounds=true

[org/gnome/desktop/interface]
gtk-theme='Arc-Dark'
icon-theme='Papirus-Dark'
EOF
command -v dconf >/dev/null 2>&1 && dconf update || true

# --- play the AetherOS startup sound once a graphical session begins ---
mkdir -p /etc/xdg/autostart
cat > /etc/xdg/autostart/aetheros-login-sound.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=AetherOS Login Sound
Exec=sh -c "canberra-gtk-play -i desktop-login 2>/dev/null || paplay /usr/share/sounds/aetheros/stereo/desktop-login.wav 2>/dev/null || true"
X-GNOME-Autostart-enabled=true
NoDisplay=true
EOF

# --- AetherOS boot splash (Plymouth) ---
if command -v plymouth-set-default-theme >/dev/null 2>&1; then
    plymouth-set-default-theme aetheros
    if [ -f /etc/mkinitcpio.conf ] && ! grep -q '\bplymouth\b' /etc/mkinitcpio.conf; then
        sed -i 's/^HOOKS=(base udev /HOOKS=(base udev plymouth /' /etc/mkinitcpio.conf
    fi
    mkinitcpio -P || true
fi

# --- Aether Cycle: enable the time-of-day wallpaper timer for every user ---
systemctl --global enable aether-cycle.timer 2>/dev/null || true

# --- enable core services ---
systemctl enable NetworkManager.service
systemctl enable lightdm.service
systemctl enable bluetooth.service
systemctl enable reflector.service 2>/dev/null || true

# --- autologin on the live medium only (real installs configure this via Calamares) ---
mkdir -p /etc/lightdm/lightdm.conf.d
cat > /etc/lightdm/lightdm.conf.d/60-live-autologin.conf <<'EOF'
[Seat:*]
autologin-user=admin
autologin-user-timeout=0
EOF

echo "==> AetherOS: airootfs customization complete."
