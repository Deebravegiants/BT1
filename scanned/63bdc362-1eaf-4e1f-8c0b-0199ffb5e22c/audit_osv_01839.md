# [H] ALPINE-CVE-2020-1737

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-1737
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-1737
Type: osv

## Affected
- Alpine:v3.10: `ansible` — affected >=0 <2.8.9-r0
- Alpine:v3.11: `ansible` — affected >=0 <2.9.6-r0
- Alpine:v3.12: `ansible` — affected >=0 <2.9.6-r0
- Alpine:v3.9: `ansible` — affected >=0 <2.7.17-r0
- Alpine:v3.13: `ansible-base` — affected >=0 <2.9.6-r0
- Alpine:v3.14: `ansible-base` — affected >=0 <2.9.6-r0

## Details
A flaw was found in Ansible 2.7.17 and prior, 2.8.9 and prior, and 2.9.6 and prior when using the Extract-Zip function from the win_unzip module as the extracted file(s) are not checked if they belong to the destination folder. An attacker could take advantage of this flaw by crafting an archive anywhere in the file system, using a path traversal. This issue is fixed in 2.10.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-1737
