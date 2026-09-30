# [C] In LibRaw before 0.21.4, phase_one_correct in decoders/load_mfbacks.cpp has out-of-bounds reads...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1110
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1110
Type: osv

## Affected
- Julia: `LibRaw_jll` — affected >=0 <0.22.1+0

## Details
In LibRaw before 0.21.4, `phase_one_correct` in `decoders/load_mfbacks.cpp` has out-of-bounds reads for tag 0x412 processing, related to large w0 or w1 values or the frac and mult calculations.

## References
- https://github.com/LibRaw/LibRaw/commit/66fe663e02a4dd610b4e832f5d9af326709336c2
- https://github.com/LibRaw/LibRaw/compare/0.21.3...0.21.4
- https://github.com/advisories/GHSA-gr77-83rx-v97c
- https://lists.debian.org/debian-lts-announce/2025/04/msg00038.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-43962
- https://www.libraw.org/news/libraw-0-21-4-release
