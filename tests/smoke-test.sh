#!/usr/bin/env bash
# =============================================================
#  AetherOS smoke test
#
#  Boots AetherOS.iso in headless QEMU using a serial console and
#  checks that the boot process reaches a usable prompt, as a basic
#  automated sanity check after every build.
#
#  Requirements: qemu-system-x86_64 (host running the test, not the
#  build sandbox — install with 'pacman -S qemu-full' or
#  'apt install qemu-system-x86').
#
#  Usage:
#     ./tests/smoke-test.sh /path/to/AetherOS.iso
# =============================================================
set -euo pipefail

ISO="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/AetherOS.iso}"
TIMEOUT="${TIMEOUT:-180}"
LOG="$(mktemp)"

[ -f "${ISO}" ] || { echo "ISO not found: ${ISO}" >&2; exit 1; }
command -v qemu-system-x86_64 >/dev/null 2>&1 || { echo "qemu-system-x86_64 not installed" >&2; exit 1; }

echo "==> Booting ${ISO} headlessly (timeout ${TIMEOUT}s)..."

timeout "${TIMEOUT}" qemu-system-x86_64 \
    -m 2048 \
    -cdrom "${ISO}" \
    -boot d \
    -nographic \
    -serial file:"${LOG}" \
    -display none \
    -no-reboot &
QEMU_PID=$!

# Poll the serial log for signs of a successful boot
success=false
for _ in $(seq 1 "${TIMEOUT}"); do
    if grep -qE "Welcome to AetherOS|aetheros login:|systemd.*reached target Graphical" "${LOG}" 2>/dev/null; then
        success=true
        break
    fi
    sleep 1
done

kill "${QEMU_PID}" 2>/dev/null || true
wait "${QEMU_PID}" 2>/dev/null || true

echo "----- last 40 lines of serial output -----"
tail -n 40 "${LOG}" || true
echo "-------------------------------------------"

if [ "${success}" = true ]; then
    echo "PASS: AetherOS reached a usable boot state."
    rm -f "${LOG}"
    exit 0
else
    echo "FAIL: did not detect a successful boot within ${TIMEOUT}s." >&2
    echo "Full log kept at: ${LOG}" >&2
    exit 1
fi
