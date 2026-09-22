# [M] ALPINE-CVE-2020-1746

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-1746
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.9
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2020-05-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-1746
Type: osv

## Affected
- Alpine:v3.11: `ansible` — affected >=0 <2.9.7-r0
- Alpine:v3.12: `ansible` — affected >=0 <2.9.7-r0
- Alpine:v3.9: `ansible` — affected >=0 <2.7.17-r0
- Alpine:v3.13: `ansible-base` — affected >=0 <2.9.7-r0
- Alpine:v3.14: `ansible-base` — affected >=0 <2.9.7-r0

## Details
A flaw was found in the Ansible Engine affecting Ansible Engine versions 2.7.x before 2.7.17 and 2.8.x before 2.8.11 and 2.9.x before 2.9.7 as well as Ansible Tower before and including versions 3.4.5 and 3.5.5 and 3.6.3 when the ldap_attr and ldap_entry community modules are used. The issue discloses the LDAP bind password to stdout or a log file if a playbook task is written using the bind_pw in the parameters field. The highest threat from this vulnerability is data confidentiality.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-1746
