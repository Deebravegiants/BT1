# [M] ALPINE-CVE-2020-14332

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-14332
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-09-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14332
Type: osv

## Affected
- Alpine:v3.10: `ansible` — affected >=0 <2.8.15-r0
- Alpine:v3.11: `ansible` — affected >=0 <2.9.13-r0
- Alpine:v3.12: `ansible` — affected >=0 <2.9.13-r0
- Alpine:v3.13: `ansible-base` — affected >=0 <2.9.13-r0
- Alpine:v3.14: `ansible-base` — affected >=0 <2.9.13-r0

## Details
A flaw was found in the Ansible Engine when using module_args. Tasks executed with check mode (--check-mode) do not properly neutralize sensitive data exposed in the event data. This flaw allows unauthorized users to read this data. The highest threat from this vulnerability is to confidentiality.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14332
