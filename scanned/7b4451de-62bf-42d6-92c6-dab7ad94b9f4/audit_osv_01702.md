# [M] ALPINE-CVE-2020-10691

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-10691
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14
CVSS: 5.2 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:L)
Published: 2020-04-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-10691
Type: osv

## Affected
- Alpine:v3.11: `ansible` — affected >=0 <2.9.7-r0
- Alpine:v3.12: `ansible` — affected >=0 <2.9.7-r0
- Alpine:v3.13: `ansible-base` — affected >=0 <2.9.7-r0
- Alpine:v3.14: `ansible-base` — affected >=0 <2.9.7-r0

## Details
An archive traversal flaw was found in all ansible-engine versions 2.9.x prior to 2.9.7, when running ansible-galaxy collection install. When extracting a collection .tar.gz file, the directory is created without sanitizing the filename. An attacker could take advantage to overwrite any file within the system.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-10691
