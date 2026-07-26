#!/usr/bin/env bash
# =============================================================
#  AetherOS docker-build.sh
#
#  Builds AetherOS.iso using Docker, so you do NOT need to be on
#  Arch Linux or install archiso on your own machine. Works on
#  Linux, macOS, and Windows (via WSL2 + Docker Desktop).
#
#  Requirements: Docker installed and running, internet access.
#
#  Usage:
#     ./docker-build.sh
#
#  Result:
#     ./AetherOS.iso
# =============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_TAG="aetheros-builder"

command -v docker >/dev/null 2>&1 || {
    echo "Docker is required. Install it from https://docs.docker.com/get-docker/ and try again." >&2
    exit 1
}

echo "==> Building the AetherOS builder image (Arch Linux + archiso)..."
docker build -t "${IMAGE_TAG}" -f "${SCRIPT_DIR}/Dockerfile" "${SCRIPT_DIR}"

echo "==> Running the build inside the container (this can take 15-40 minutes)..."
docker run --rm --privileged \
    -v "${SCRIPT_DIR}:/aetheros" \
    -w /aetheros \
    "${IMAGE_TAG}"

if [ -f "${SCRIPT_DIR}/AetherOS.iso" ]; then
    echo "==> Done! AetherOS.iso is in: ${SCRIPT_DIR}"
else
    echo "Build finished but AetherOS.iso was not found — check the log above for errors." >&2
    exit 1
fi
