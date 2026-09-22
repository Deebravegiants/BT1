# [M] ALPINE-CVE-2018-14056

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-14056
Ecosystem: Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-07-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14056
Type: osv

## Affected
- Alpine:v3.5: `znc` — affected >=0 <1.7.1-r0
- Alpine:v3.6: `znc` — affected >=0 <1.7.1-r0
- Alpine:v3.7: `znc` — affected >=0 <1.7.1-r0
- Alpine:v3.8: `znc` — affected >=0 <1.7.1-r0

## Details
ZNC before 1.7.1-rc1 is prone to a path traversal flaw via ../ in a web skin name to access files outside of the intended skins directories.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14056
