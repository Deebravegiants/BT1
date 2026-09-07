# [H] Phantom: Arbitrary file write and decode-bomb DoS via unconfined MCP tool paths

## Summary
Severity: High
Advisory: GHSA-52vm-mxx8-f227
CWE: CWE-22, CWE-400, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-52vm-mxx8-f227
Type: github-advisory

## Affected
- PyPI: `phantom-audio` — affected >=0 <1.3.1

## Details
### Impact

In Phantom <= 1.3.0, when `PHANTOM_OUTPUT_DIR` was unset (the default), the MCP tools accepted arbitrary absolute output paths with no confinement. Anything able to send tool calls (e.g. an AI agent driving the MCP interface) could **write or overwrite arbitrary files** the process user can write — including shell startup files (`~/.zshrc`) or a Reaper `__startup.lua`, which is effectively local code execution on a developer workstation.

Separately, the stem-separation and render paths decoded input audio with no size/duration cap (the analysis path was already guarded). A small, highly compressed FLAC/OGG could expand to multi-gigabyte PCM, causing memory-exhaustion DoS, and widened exposure to decoder bugs including libsndfile CVE-2026-37555.

### Patches
Fixed in **1.3.1**:
- File writes are always confined to `PHANTOM_OUTPUT_DIR` (default `~/.phantom/output`); symlinks resolved and re-verified on the final path.
- Decode/duration/size guards mirrored onto the separation and render paths (plus ffmpeg `-max_alloc`/`-t`/`-fs`).
- Atomic `O_CREAT|O_EXCL` output creation in reference matching and symlink-TOCTOU hardening on confined input reads.

### Workarounds
Set `PHANTOM_OUTPUT_DIR` (and optionally `PHANTOM_AUDIO_DIR`) to dedicated directories before starting the server.

### Credit
Found during an internal security audit.

## References
- https://github.com/fadelabs/phantom/security/advisories/GHSA-52vm-mxx8-f227
- https://github.com/fadelabs/phantom
