# [M] ALPINE-CVE-2019-9959

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-9959
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-9959
Type: osv

## Affected
- Alpine:v3.10: `poppler` — affected >=0 <0.71.0-r1
- Alpine:v3.11: `poppler` — affected >=0 <0.80.0-r0
- Alpine:v3.12: `poppler` — affected >=0 <0.80.0-r0
- Alpine:v3.13: `poppler` — affected >=0 <0.80.0-r0
- Alpine:v3.14: `poppler` — affected >=0 <0.80.0-r0
- Alpine:v3.15: `poppler` — affected >=0 <0.80.0-r0
- Alpine:v3.16: `poppler` — affected >=0 <0.80.0-r0
- Alpine:v3.17: `poppler` — affected >=0 <0.80.0-r0
- Alpine:v3.18: `poppler` — affected >=0 <0.80.0-r0
- Alpine:v3.19: `poppler` — affected >=0 <0.80.0-r0
- Alpine:v3.20: `poppler` — affected >=0 <0.80.0-r0
- Alpine:v3.21: `poppler` — affected >=0 <0.80.0-r0
- Alpine:v3.22: `poppler` — affected >=0 <0.80.0-r0
- Alpine:v3.23: `poppler` — affected >=0 <0.80.0-r0
- Alpine:v3.24: `poppler` — affected >=0 <0.80.0-r0
- Alpine:v3.7: `poppler` — affected >=0 <0.56.0-r1
- Alpine:v3.8: `poppler` — affected >=0 <0.56.0-r2
- Alpine:v3.9: `poppler` — affected >=0 <0.56.0-r2

## Details
The JPXStream::init function in Poppler 0.78.0 and earlier doesn't check for negative values of stream length, leading to an Integer Overflow, thereby making it possible to allocate a large memory chunk on the heap, with a size controlled by an attacker, as demonstrated by pdftocairo.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-9959
