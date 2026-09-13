# [H] ALPINE-CVE-2018-10875

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-10875
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-10875
Type: osv

## Affected
- Alpine:v3.10: `ansible` — affected >=0 <2.6.3-r0
- Alpine:v3.11: `ansible` — affected >=0 <2.6.3-r0
- Alpine:v3.12: `ansible` — affected >=0 <2.6.3-r0
- Alpine:v3.9: `ansible` — affected >=0 <2.6.3-r0
- Alpine:v3.13: `ansible-base` — affected >=0 <2.6.3-r0
- Alpine:v3.14: `ansible-base` — affected >=0 <2.6.3-r0

## Details
A flaw was found in ansible. ansible.cfg is read from the current working directory which can be altered to make it point to a plugin or a module path under the control of an attacker, thus allowing the attacker to execute arbitrary code.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-10875
