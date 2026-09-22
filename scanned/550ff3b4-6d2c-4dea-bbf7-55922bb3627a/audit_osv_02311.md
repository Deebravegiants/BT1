# [H] ALPINE-CVE-2021-42341

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-42341
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-42341
Type: osv

## Affected
- Alpine:v3.14: `openrc` — affected >=0.44.0 <0.43.3-r2
- Alpine:v3.15: `openrc` — affected >=0.44.0 <0.44.6-r1
- Alpine:v3.16: `openrc` — affected >=0.44.0 <0.44.6-r1
- Alpine:v3.17: `openrc` — affected >=0.44.0 <0.44.6-r1
- Alpine:v3.18: `openrc` — affected >=0.44.0 <0.44.6-r1
- Alpine:v3.19: `openrc` — affected >=0.44.0 <0.44.6-r1
- Alpine:v3.20: `openrc` — affected >=0.44.0 <0.44.6-r1
- Alpine:v3.21: `openrc` — affected >=0.44.0 <0.44.6-r1
- Alpine:v3.22: `openrc` — affected >=0.44.0 <0.44.6-r1
- Alpine:v3.23: `openrc` — affected >=0.44.0 <0.44.6-r1
- Alpine:v3.24: `openrc` — affected >=0.44.0 <0.44.6-r1

## Details
checkpath in OpenRC before 0.44.7 uses the direct output of strlen() to allocate strings, which does not account for the '\0' byte at the end of the string. This results in memory corruption. CVE-2021-42341 was introduced in git commit 63db2d99e730547339d1bdd28e8437999c380cae, which was introduced as part of OpenRC 0.44.0 development.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-42341
