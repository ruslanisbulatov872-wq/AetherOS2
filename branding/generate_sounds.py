#!/usr/bin/env python3
"""
Synthesizes AetherOS's 5 system sounds as real .wav files, entirely offline,
using only Python's standard library (wave + math). No samples are
downloaded or copied from anywhere — every waveform is generated here.

Design goal: soft, warm, "with a bit of soul" — layered sine harmonics with
smooth attack/decay envelopes, not flat single-frequency beeps.

Usage:
    python3 generate_sounds.py

Outputs into ../profile/airootfs/usr/share/sounds/aetheros/stereo/
"""
import math
import os
import struct
import wave

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(ROOT, "..", "profile", "airootfs", "usr", "share", "sounds", "aetheros", "stereo")

SAMPLE_RATE = 44100


def envelope(t, duration, attack=0.02, release=0.35):
    """Smooth volume envelope: quick fade-in, gentle exponential fade-out —
    avoids clicks and harshness at the start/end of every sound."""
    if t < attack:
        return t / attack
    remain = duration - t
    if remain < release:
        return max(0.0, remain / release) ** 1.5
    return 1.0


def tone(freq, duration, amp=0.28, harmonics=((1, 1.0), (2, 0.18), (3, 0.06))):
    """One warm tone: a fundamental plus a couple of quiet harmonics so it
    doesn't sound like a flat sine-wave beep."""
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = envelope(t, duration)
        s = 0.0
        for mult, hamp in harmonics:
            s += hamp * math.sin(2 * math.pi * freq * mult * t)
        samples.append(s * amp * env)
    return samples


def chord(freqs, duration, amp=0.22):
    """Several tones layered together (a soft chord), each with its own
    envelope, mixed down."""
    n = int(SAMPLE_RATE * duration)
    mix = [0.0] * n
    for freq in freqs:
        t_samples = tone(freq, duration, amp=amp)
        for i in range(n):
            mix[i] += t_samples[i]
    peak = max(1e-9, max(abs(x) for x in mix))
    if peak > 0.9:
        mix = [x * 0.9 / peak for x in mix]
    return mix


def sequence(*parts):
    """Concatenate (tone/chord, gap_seconds) parts into one sample list."""
    out = []
    for samples, gap in parts:
        out.extend(samples)
        out.extend([0.0] * int(SAMPLE_RATE * gap))
    return out


def write_wav(path, samples, stereo=True):
    n = len(samples)
    with wave.open(path, "w") as wf:
        wf.setnchannels(2 if stereo else 1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for s in samples:
            v = max(-1.0, min(1.0, s))
            iv = int(v * 32767)
            packed = struct.pack("<h", iv)
            frames += packed * (2 if stereo else 1)
        wf.writeframes(bytes(frames))


# --- musical helpers: simple equal-temperament note -> frequency ----------
A4 = 440.0

def note(name, octave):
    order = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    n = order.index(name) + (octave - 4) * 12 - 9  # semitones from A4
    return A4 * (2 ** (n / 12))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # 1) Startup — gentle rising major arpeggio, like a soft sunrise chime
    startup = sequence(
        (tone(note("C", 4), 0.35, amp=0.22), 0.03),
        (tone(note("E", 4), 0.35, amp=0.24), 0.03),
        (tone(note("G", 4), 0.45, amp=0.26), 0.05),
        (chord([note("C", 5), note("G", 4), note("E", 4)], 0.9, amp=0.16), 0.0),
    )
    write_wav(os.path.join(OUT_DIR, "desktop-login.wav"), startup)

    # 2) Error — soft two-note descending minor second, calm but distinct
    error = sequence(
        (tone(note("A", 4), 0.16, amp=0.24, harmonics=((1, 1.0), (2, 0.12))), 0.05),
        (tone(note("F", 4), 0.30, amp=0.22, harmonics=((1, 1.0), (2, 0.12))), 0.0),
    )
    write_wav(os.path.join(OUT_DIR, "dialog-error.wav"), error)

    # 3) System requirement / privilege prompt (sudo, install confirm, etc.)
    #    — a single warm, attention-getting but non-jarring chord
    system_req = sequence(
        (chord([note("D", 4), note("A", 4), note("D", 5)], 0.5, amp=0.24), 0.0),
    )
    write_wav(os.path.join(OUT_DIR, "dialog-warning.wav"), system_req)

    # 4) Signature sound (AetherOS's own) — a little melodic flourish,
    #    used for "task complete" / achievement-style events
    signature = sequence(
        (tone(note("E", 4), 0.14, amp=0.22), 0.01),
        (tone(note("G", 4), 0.14, amp=0.22), 0.01),
        (tone(note("B", 4), 0.14, amp=0.22), 0.01),
        (chord([note("E", 5), note("B", 4)], 0.55, amp=0.18), 0.0),
    )
    write_wav(os.path.join(OUT_DIR, "complete.wav"), signature)

    # 5) Notification — one short, soft blip (two quiet harmonics, quick decay)
    notif = tone(note("C", 5), 0.22, amp=0.20, harmonics=((1, 1.0), (2, 0.10)))
    write_wav(os.path.join(OUT_DIR, "message.wav"), notif)

    print("Generated 5 AetherOS sounds in:", OUT_DIR)
    for f in ("desktop-login.wav", "dialog-error.wav", "dialog-warning.wav", "complete.wav", "message.wav"):
        print(" -", f)


if __name__ == "__main__":
    main()
