# [C] ALPINE-CVE-2026-4176

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-4176
Ecosystem: Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-4176
Type: osv

## Affected
- Alpine:v3.24: `perl` — affected >=5.9.4 <5.42.2-r0

## Details
Perl versions from 5.9.4 before 5.40.4-RC1, from 5.41.0 before 5.42.2-RC1, from 5.43.0 before 5.43.9 contain a vulnerable version of Compress::Raw::Zlib.

Compress::Raw::Zlib is included in the Perl package as a dual-life core module, and is vulnerable to CVE-2026-3381 due to a vendored version of zlib which has several vulnerabilities, including CVE-2026-27171. The bundled Compress::Raw::Zlib was updated to version 2.221 in Perl blead commit c75ae9cc164205e1b6d6dbd57bd2c65c8593fe94.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-4176
