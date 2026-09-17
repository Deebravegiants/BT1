# [H] ALPINE-CVE-2018-8791

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-8791
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-02-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-8791
Type: osv

## Affected
- Alpine:v3.10: `rdesktop` — affected >=0 <1.8.6-r0
- Alpine:v3.11: `rdesktop` — affected >=0 <1.8.6-r0
- Alpine:v3.12: `rdesktop` — affected >=0 <1.8.6-r0
- Alpine:v3.13: `rdesktop` — affected >=0 <1.8.6-r0
- Alpine:v3.14: `rdesktop` — affected >=0 <1.8.6-r0

## Details
rdesktop versions up to and including v1.8.3 contain an Out-Of-Bounds Read in function rdpdr_process() that results in an information leak.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-8791
