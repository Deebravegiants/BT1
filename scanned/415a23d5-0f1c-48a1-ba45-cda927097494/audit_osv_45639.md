# [M] JLSEC-2026-153

## Summary
Severity: Medium
Advisory: JLSEC-2026-153
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/JLSEC-2026-153
Type: osv

## Affected
- Julia: `LibArchive_jll` — affected >=0 <3.8.2+0

## Details
An issue was discovered in libarchive bsdtar before version 3.8.1 in function `apply_substitution` in file `tar/subst.c` when processing crafted -s substitution rules. This can cause unbounded memory allocation and lead to denial of service (Out-of-Memory crash).

## References
- https://github.com/Papya-j/CVE/tree/main/CVE-2025-60753
- https://github.com/libarchive/libarchive/issues/2725
