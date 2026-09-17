# [H] JLSEC-2026-79

## Summary
Severity: High
Advisory: JLSEC-2026-79
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-11
Source: https://osv.dev/vulnerability/JLSEC-2026-79
Type: osv

## Affected
- Julia: `Fontconfig_jll` — affected >=0 <2.17.1+0

## Details
fontconfig before 2.17.1 has an off-by-one error in allocation during sfnt capability handling, leading to a one-byte out-of-bounds write, and potentially a crash or code execution. This is in FcFontCapabilities in fcfreetype.c.

## References
- https://gitlab.freedesktop.org/fontconfig/fontconfig/-/commit/b9bec06d73340f1b5727302d13ac3df307b7febc
- https://gitlab.freedesktop.org/fontconfig/fontconfig/-/merge_requests/446
- https://gitlab.freedesktop.org/fontconfig/fontconfig/-/work_items/481
