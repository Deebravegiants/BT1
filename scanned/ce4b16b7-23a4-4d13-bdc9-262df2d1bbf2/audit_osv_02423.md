# [C] ALPINE-CVE-2022-22817

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-22817
Ecosystem: Alpine:v3.15
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-22817
Type: osv

## Affected
- Alpine:v3.15: `py3-pillow` — affected >=0 <8.4.0-r3

## Details
PIL.ImageMath.eval in Pillow before 9.0.0 allows evaluation of arbitrary expressions, such as ones that use the Python exec method. A lambda expression could also be used.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-22817
