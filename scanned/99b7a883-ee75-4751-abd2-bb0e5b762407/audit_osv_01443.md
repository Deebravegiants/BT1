# [H] ALPINE-CVE-2019-14846

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-14846
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-14846
Type: osv

## Affected
- Alpine:v3.10: `ansible` — affected >=0 <2.8.6-r0
- Alpine:v3.11: `ansible` — affected >=0 <2.9.13-r0
- Alpine:v3.12: `ansible` — affected >=0 <2.9.13-r0
- Alpine:v3.8: `ansible` — affected >=0 <2.6.20-r0
- Alpine:v3.9: `ansible` — affected >=0 <2.7.14-r0
- Alpine:v3.13: `ansible-base` — affected >=0 <2.8.6-r0
- Alpine:v3.14: `ansible-base` — affected >=0 <2.8.6-r0

## Details
In Ansible, all Ansible Engine versions up to ansible-engine 2.8.5, ansible-engine 2.7.13, ansible-engine 2.6.19, were logging at the DEBUG level which lead to a disclosure of credentials if a plugin used a library that logged credentials at the DEBUG level. This flaw does not affect Ansible modules, as those are executed in a separate process.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-14846
