# [H] ALPINE-CVE-2019-14904

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-14904
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.9
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:L/A:L)
Published: 2020-08-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-14904
Type: osv

## Affected
- Alpine:v3.10: `ansible` — affected >=2.8.0 <2.8.8-r0
- Alpine:v3.11: `ansible` — affected >=2.8.0 <2.9.3-r0
- Alpine:v3.12: `ansible` — affected >=2.8.0 <2.9.3-r0
- Alpine:v3.9: `ansible` — affected >=2.8.0 <2.7.16-r0
- Alpine:v3.13: `ansible-base` — affected >=0 <2.9.3-r0
- Alpine:v3.14: `ansible-base` — affected >=0 <2.9.3-r0

## Details
A flaw was found in the solaris_zone module from the Ansible Community modules. When setting the name for the zone on the Solaris host, the zone name is checked by listing the process with the 'ps' bare command on the remote machine. An attacker could take advantage of this flaw by crafting the name of the zone and executing arbitrary commands in the remote host. Ansible Engine 2.7.15, 2.8.7, and 2.9.2 as well as previous versions are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-14904
