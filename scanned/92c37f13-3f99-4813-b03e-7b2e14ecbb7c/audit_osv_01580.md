# [M] ALPINE-CVE-2019-3828

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-3828
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.8, Alpine:v3.9
CVSS: 4.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-03-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-3828
Type: osv

## Affected
- Alpine:v3.10: `ansible` — affected >=2.5.0 <2.8.11-r0
- Alpine:v3.11: `ansible` — affected >=2.5.0 <2.9.7-r0
- Alpine:v3.12: `ansible` — affected >=2.5.0 <2.9.7-r0
- Alpine:v3.8: `ansible` — affected >=2.5.0 <2.5.15-r0
- Alpine:v3.9: `ansible` — affected >=2.5.0 <2.7.17-r0
- Alpine:v3.13: `ansible-base` — affected >=0 <2.9.7-r0
- Alpine:v3.14: `ansible-base` — affected >=0 <2.9.7-r0

## Details
Ansible fetch module before versions 2.5.15, 2.6.14, 2.7.8 has a path traversal vulnerability which allows copying and overwriting files outside of the specified destination in the local ansible controller host, by not restricting an absolute path.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-3828
