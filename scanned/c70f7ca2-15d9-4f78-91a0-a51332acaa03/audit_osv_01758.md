# [M] ALPINE-CVE-2020-14330

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-14330
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-09-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14330
Type: osv

## Affected
- Alpine:v3.10: `ansible` — affected >=0 <2.8.15-r0
- Alpine:v3.11: `ansible` — affected >=0 <2.9.13-r0
- Alpine:v3.12: `ansible` — affected >=0 <2.9.13-r0
- Alpine:v3.13: `ansible-base` — affected >=0 <2.9.13-r0
- Alpine:v3.14: `ansible-base` — affected >=0 <2.9.13-r0

## Details
An Improper Output Neutralization for Logs flaw was found in Ansible when using the uri module, where sensitive data is exposed to content and json output. This flaw allows an attacker to access the logs or outputs of performed tasks to read keys used in playbooks from other users within the uri module. The highest threat from this vulnerability is to data confidentiality.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14330
