# [H] ALPINE-CVE-2020-14365

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-14365
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2020-09-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14365
Type: osv

## Affected
- Alpine:v3.10: `ansible` — affected >=0 <2.8.15-r0
- Alpine:v3.11: `ansible` — affected >=0 <2.9.13-r0
- Alpine:v3.12: `ansible` — affected >=0 <2.9.13-r0
- Alpine:v3.13: `ansible-base` — affected >=0 <2.9.13-r0
- Alpine:v3.14: `ansible-base` — affected >=0 <2.9.13-r0

## Details
A flaw was found in the Ansible Engine, in ansible-engine 2.8.x before 2.8.15 and ansible-engine 2.9.x before 2.9.13, when installing packages using the dnf module. GPG signatures are ignored during installation even when disable_gpg_check is set to False, which is the default behavior. This flaw leads to malicious packages being installed on the system and arbitrary code executed via package installation scripts. The highest threat from this vulnerability is to integrity and system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14365
