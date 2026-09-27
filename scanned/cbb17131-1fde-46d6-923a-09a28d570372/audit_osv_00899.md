# [M] ALPINE-CVE-2018-10855

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-10855
Ecosystem: Alpine:v3.7
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-10855
Type: osv

## Affected
- Alpine:v3.7: `ansible` — affected >=0 <2.4.6.0-r0

## Details
Ansible 2.5 prior to 2.5.5, and 2.4 prior to 2.4.5, do not honor the no_log task flag for failed tasks. When the no_log flag has been used to protect sensitive data passed to a task from being logged, and that task does not run successfully, Ansible will expose sensitive data in log files and on the terminal of the user running Ansible.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-10855
