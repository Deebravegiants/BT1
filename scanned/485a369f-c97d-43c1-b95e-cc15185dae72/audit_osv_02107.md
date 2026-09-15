# [H] ALPINE-CVE-2021-23437

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-23437
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-09-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-23437
Type: osv

## Affected
- Alpine:v3.11: `py-pillow` — affected >=0 <6.2.1-r1
- Alpine:v3.12: `py3-pillow` — affected >=0 <7.1.2-r2
- Alpine:v3.13: `py3-pillow` — affected >=0 <7.2.0-r2
- Alpine:v3.14: `py3-pillow` — affected >=0 <8.2.0-r1
- Alpine:v3.15: `py3-pillow` — affected >=0 <8.4.0-r0

## Details
The package pillow 5.2.0 and before 8.3.2 are vulnerable to Regular Expression Denial of Service (ReDoS) via the getrgb function.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-23437
