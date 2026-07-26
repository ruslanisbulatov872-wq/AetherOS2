#!/usr/bin/env bash
# =============================================================
#  AetherOS build.sh — fully automated ISO builder
#
#  Run this on an Arch Linux machine (bare metal, VM, or the
#  archlinux Docker image) with an internet connection.
#  If you are NOT on Arch Linux, use ./docker-build.sh instead —
#  it does the exact same thing inside an Arch Linux container,
#  so you don't need to install anything on your host OS.
#
#  Usage:
#     ./build.sh
#
#  Result:
#     ./out/AetherOS.iso
# =============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_DIR="${SCRIPT_DIR}/profile"
WORK_DIR="${SCRIPT_DIR}/work"
OUT_DIR="${SCRIPT_DIR}/out"

log()  { printf '\033[1;34m==>\033[0m %s\n' "$1"; }
die()  { printf '\033[1;31mERROR:\033[0m %s\n' "$1" >&2; exit 1; }

# --- 1. sanity checks -----------------------------------------------------
[ -f /etc/arch-release ] || die "This script must run on Arch Linux (or use ./docker-build.sh)."
[ "$(id -u)" -eq 0 ] || die "Please run as root (sudo ./build.sh)."
[ -d "${PROFILE_DIR}" ] || die "profile/ directory not found next to build.sh"

log "AetherOS build starting..."

# --- 2. dependencies -------------------------------------------------------
log "Checking / installing build dependencies (archiso, git, base-devel, grub, syslinux)..."
pacman -Sy --needed --noconfirm archiso git base-devel grub syslinux dosfstools mtools

# --- 2a. Chaotic-AUR (needed to fetch calamares / arc-gtk-theme, which are
#         AUR-only nowadays) -------------------------------------------------
if ! pacman -Q chaotic-keyring >/dev/null 2>&1; then
    log "Setting up Chaotic-AUR (for calamares / arc-gtk-theme)..."
    pacman-key --recv-key 3056513887B78AEB --keyserver keyserver.ubuntu.com
    pacman-key --lsign-key 3056513887B78AEB
    pacman -U --noconfirm \
        'https://cdn-mirror.chaotic.cx/chaotic-aur/chaotic-keyring.pkg.tar.zst' \
        'https://cdn-mirror.chaotic.cx/chaotic-aur/chaotic-mirrorlist.pkg.tar.zst'
fi

# --- 2b. bootloader templates -----------------------------------------------
# mkarchiso needs profile/syslinux/ and profile/grub/ with bootloader config
# templates. If this profile doesn't have them yet, seed them from the
# official archiso "releng" example that ships inside the archiso package.
RELENG_CONFIGS="/usr/share/archiso/configs/releng"
if [ ! -d "${PROFILE_DIR}/syslinux" ] && [ -d "${RELENG_CONFIGS}/syslinux" ]; then
    log "profile/syslinux/ missing — copying default templates from archiso's releng profile..."
    cp -r "${RELENG_CONFIGS}/syslinux" "${PROFILE_DIR}/syslinux"
fi
if [ ! -d "${PROFILE_DIR}/grub" ] && [ -d "${RELENG_CONFIGS}/grub" ]; then
    log "profile/grub/ missing — copying default templates from archiso's releng profile..."
    cp -r "${RELENG_CONFIGS}/grub" "${PROFILE_DIR}/grub"
fi

# --- 3. clean previous build artifacts -------------------------------------
log "Cleaning previous work/out directories..."
rm -rf "${WORK_DIR}" "${OUT_DIR}"
mkdir -p "${OUT_DIR}"

# --- 4. sanity-check the profile syntax before a (long) real build --------
log "Validating profile scripts..."
bash -n "${PROFILE_DIR}/profiledef.sh"
find "${PROFILE_DIR}/airootfs" -type f -name '*.sh' -print0 | while IFS= read -r -d '' f; do
    bash -n "$f" || die "Syntax error in $f"
done

# --- 5. build the ISO with mkarchiso ---------------------------------------
log "Building the ISO with mkarchiso (this can take 15-40 minutes)..."
mkarchiso -v -w "${WORK_DIR}" -o "${OUT_DIR}" "${PROFILE_DIR}"

# --- 6. rename to the friendly final name ----------------------------------
built_iso="$(find "${OUT_DIR}" -maxdepth 1 -name '*.iso' | head -n1)"
[ -n "${built_iso}" ] || die "mkarchiso finished but no .iso file was found in ${OUT_DIR}"
final_iso="${SCRIPT_DIR}/AetherOS.iso"
mv -f "${built_iso}" "${final_iso}"

# --- 7. clean up the (large) work directory --------------------------------
log "Cleaning up build cache..."
rm -rf "${WORK_DIR}"

log "Done! Your ISO is ready at:"
echo "   ${final_iso}"
echo
echo "Test it with:"
echo "   qemu-system-x86_64 -enable-kvm -m 4096 -cdrom '${final_iso}'"
echo "Or open it directly in VirtualBox as a virtual optical disk."
