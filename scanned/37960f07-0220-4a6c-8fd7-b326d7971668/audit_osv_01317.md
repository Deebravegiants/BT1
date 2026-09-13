# [M] ALPINE-CVE-2019-10156

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-10156
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.8
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2019-07-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-10156
Type: osv

## Affected
- Alpine:v3.10: `ansible` — affected >=2.7.0 <2.8.2-r0
- Alpine:v3.11: `ansible` — affected >=2.7.0 <2.8.2-r0
- Alpine:v3.12: `ansible` — affected >=2.7.0 <2.8.2-r0
- Alpine:v3.8: `ansible` — affected >=2.7.0 <2.6.18-r0
- Alpine:v3.13: `ansible-base` — affected >=0 <2.8.2-r0
- Alpine:v3.14: `ansible-base` — affected >=0 <2.8.2-r0

## Details
A flaw was discovered in the way Ansible templating was implemented in versions before 2.6.18, 2.7.12 and 2.8.2, causing the possibility of information disclosure through unexpected variable substitution. By taking advantage of unintended variable substitution the content of any variable may be disclosed.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-10156
