# [M] ALPINE-CVE-2018-21269

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-21269
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-10-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-21269
Type: osv

## Affected
- Alpine:v3.10: `openrc` — affected >=0 <0.41.2-r2
- Alpine:v3.11: `openrc` — affected >=0 <0.42.1-r3
- Alpine:v3.12: `openrc` — affected >=0 <0.42.1-r12
- Alpine:v3.13: `openrc` — affected >=0 <0.42.1-r20

## Details
checkpath in OpenRC through 0.42.1 might allow local users to take ownership of arbitrary files because a non-terminal path component can be a symlink.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-21269
