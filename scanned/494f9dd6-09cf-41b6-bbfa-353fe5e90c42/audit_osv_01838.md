# [M] ALPINE-CVE-2020-1733

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-1733
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.9
CVSS: 5.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:L)
Published: 2020-03-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-1733
Type: osv

## Affected
- Alpine:v3.10: `ansible` — affected >=2.8.0 <2.8.11-r0
- Alpine:v3.11: `ansible` — affected >=2.8.0 <2.9.7-r0
- Alpine:v3.12: `ansible` — affected >=2.8.0 <2.9.7-r0
- Alpine:v3.9: `ansible` — affected >=2.8.0 <2.7.17-r0
- Alpine:v3.13: `ansible-base` — affected >=0 <2.9.7-r0
- Alpine:v3.14: `ansible-base` — affected >=0 <2.9.7-r0

## Details
A race condition flaw was found in Ansible Engine 2.7.17 and prior, 2.8.9 and prior, 2.9.6 and prior when running a playbook with an unprivileged become user. When Ansible needs to run a module with become user, the temporary directory is created in /var/tmp. This directory is created with "umask 77 && mkdir -p <dir>"; this operation does not fail if the directory already exists and is owned by another user. An attacker could take advantage to gain control of the become user as the target directory can be retrieved by iterating '/proc/<pid>/cmdline'.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-1733
