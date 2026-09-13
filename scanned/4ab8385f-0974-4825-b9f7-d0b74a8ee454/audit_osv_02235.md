# [C] ALPINE-CVE-2021-34552

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-34552
Ecosystem: Alpine:v3.15
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-34552
Type: osv

## Affected
- Alpine:v3.15: `py3-pillow` — affected >=0 <8.3.0-r0

## Details
Pillow through 8.2.0 and PIL (aka Python Imaging Library) through 1.1.7 allow an attacker to pass controlled parameters directly into a convert function to trigger a buffer overflow in Convert.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-34552
