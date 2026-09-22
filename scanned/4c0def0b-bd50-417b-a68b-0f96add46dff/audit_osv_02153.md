# [M] ALPINE-CVE-2021-28675

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-28675
Ecosystem: Alpine:v3.14, Alpine:v3.15
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28675
Type: osv

## Affected
- Alpine:v3.14: `py3-pillow` — affected >=0 <8.2.0-r0
- Alpine:v3.15: `py3-pillow` — affected >=0 <8.2.0-r0

## Details
An issue was discovered in Pillow before 8.2.0. PSDImagePlugin.PsdImageFile lacked a sanity check on the number of input layers relative to the size of the data block. This could lead to a DoS on Image.open prior to Image.load.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28675
