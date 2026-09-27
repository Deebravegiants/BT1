# [M] ALPINE-CVE-2019-14858

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-14858
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-10-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-14858
Type: osv

## Affected
- Alpine:v3.10: `ansible` — affected >=0 <2.8.6-r0
- Alpine:v3.11: `ansible` — affected >=0 <2.8.6-r0
- Alpine:v3.12: `ansible` — affected >=0 <2.8.6-r0
- Alpine:v3.8: `ansible` — affected >=0 <2.6.20-r0
- Alpine:v3.9: `ansible` — affected >=0 <2.7.14-r0
- Alpine:v3.13: `ansible-base` — affected >=0 <2.8.6-r0
- Alpine:v3.14: `ansible-base` — affected >=0 <2.8.6-r0

## Details
A vulnerability was found in Ansible engine 2.x up to 2.8 and Ansible tower 3.x up to 3.5. When a module has an argument_spec with sub parameters marked as no_log, passing an invalid parameter name to the module will cause the task to fail before the no_log options in the sub parameters are processed. As a result, data in the sub parameter fields will not be masked and will be displayed if Ansible is run with increased verbosity and present in the module invocation arguments for the task.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-14858
