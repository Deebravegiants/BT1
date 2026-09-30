# [C] In LibRaw before 0.21.4, phase_one_correct in decoders/load_mfbacks.cpp allows out-of-buffer...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1111
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1111
Type: osv

## Affected
- Julia: `LibRaw_jll` — affected >=0 <0.22.1+0

## Details
In LibRaw before 0.21.4, `phase_one_correct` in `decoders/load_mfbacks.cpp` allows out-of-buffer access because `split_col` and `split_row` values are not checked in 0x041f tag processing.

## References
- https://github.com/LibRaw/LibRaw/commit/be26e7639ecf8beb55f124ce780e99842de2e964
- https://github.com/LibRaw/LibRaw/compare/0.21.3...0.21.4
- https://github.com/advisories/GHSA-3w5w-m35v-rfp7
- https://lists.debian.org/debian-lts-announce/2025/04/msg00038.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-43963
- https://www.libraw.org/news/libraw-0-21-4-release
