# [C] In LibRaw before 0.21.4, tag 0x412 processing in phase_one_correct in decoders/load_mfbacks.cpp...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1112
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1112
Type: osv

## Affected
- Julia: `LibRaw_jll` — affected >=0 <0.22.1+0

## Details
In LibRaw before 0.21.4, tag 0x412 processing in `phase_one_correct` in `decoders/load_mfbacks.cpp` does not enforce minimum w0 and w1 values.

## References
- https://github.com/LibRaw/LibRaw/commit/a50dc3f1127d2e37a9b39f57ad9bb2ebb60f18c0
- https://github.com/LibRaw/LibRaw/compare/0.21.3...0.21.4
- https://github.com/advisories/GHSA-3cxc-phxh-65vq
- https://lists.debian.org/debian-lts-announce/2025/04/msg00038.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-43964
- https://www.libraw.org/news/libraw-0-21-4-release
