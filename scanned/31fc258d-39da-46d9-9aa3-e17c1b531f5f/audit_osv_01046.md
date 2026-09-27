# [M] ALPINE-CVE-2018-16859

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-16859
Ecosystem: Alpine:v3.9
CVSS: 4.4 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-11-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-16859
Type: osv

## Affected
- Alpine:v3.9: `ansible` — affected >=0 <2.7.3-r0

## Details
Execution of Ansible playbooks on Windows platforms with PowerShell ScriptBlock logging and Module logging enabled can allow for 'become' passwords to appear in EventLogs in plaintext. A local user with administrator privileges on the machine can view these logs and discover the plaintext password. Ansible Engine 2.8 and older are believed to be vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-16859
