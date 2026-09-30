# [M] ALPINE-CVE-2020-1740

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-1740
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.9
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-03-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-1740
Type: osv

## Affected
- Alpine:v3.10: `ansible` — affected >=2.8.0 <2.8.11-r0
- Alpine:v3.11: `ansible` — affected >=2.8.0 <2.9.7-r0
- Alpine:v3.12: `ansible` — affected >=2.8.0 <2.9.7-r0
- Alpine:v3.9: `ansible` — affected >=2.8.0 <2.7.17-r0
- Alpine:v3.13: `ansible-base` — affected >=0 <2.9.7-r0
- Alpine:v3.14: `ansible-base` — affected >=0 <2.9.7-r0

## Details
A flaw was found in Ansible Engine when using Ansible Vault for editing encrypted files. When a user executes "ansible-vault edit", another user on the same computer can read the old and new secret, as it is created in a temporary file with mkstemp and the returned file descriptor is closed and the method write_data is called to write the existing secret in the file. This method will delete the file before recreating it insecurely. All versions in 2.7.x, 2.8.x and 2.9.x branches are believed to be vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-1740
