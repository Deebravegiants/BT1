# [H] ALPINE-CVE-2018-20176

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-20176
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-20176
Type: osv

## Affected
- Alpine:v3.10: `rdesktop` — affected >=0 <1.8.6-r0
- Alpine:v3.11: `rdesktop` — affected >=0 <1.8.6-r0
- Alpine:v3.12: `rdesktop` — affected >=0 <1.8.6-r0
- Alpine:v3.13: `rdesktop` — affected >=0 <1.8.6-r0
- Alpine:v3.14: `rdesktop` — affected >=0 <1.8.6-r0

## Details
rdesktop versions up to and including v1.8.3 contain several Out-Of- Bounds Reads in the file secure.c that result in a Denial of Service (segfault).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-20176
