# [H] ALPINE-CVE-2026-76956

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-76956
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-76956
Type: osv

## Affected
- Alpine:v3.21: `expat` — affected >=0 <2.8.4-r0
- Alpine:v3.22: `expat` — affected >=0 <2.8.4-r0
- Alpine:v3.23: `expat` — affected >=0 <2.8.4-r0
- Alpine:v3.24: `expat` — affected >=0 <2.8.4-r0

## Details
In libexpat 2.8.2 and 2.8.3 before 2.8.4, misinterpretation of getentropy's return code leads to insufficient entropy, which results in being vulnerable to hash flooding attacks, causing a denial of service via crafted XML content.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-76956
