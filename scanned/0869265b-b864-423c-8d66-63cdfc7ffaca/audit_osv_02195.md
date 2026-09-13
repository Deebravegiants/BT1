# [H] ALPINE-CVE-2021-31566

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-31566
Ecosystem: Alpine:v3.13, Alpine:v3.14
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-08-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-31566
Type: osv

## Affected
- Alpine:v3.13: `libarchive` — affected >=0 <3.5.3-r0
- Alpine:v3.14: `libarchive` — affected >=0 <3.5.3-r0

## Details
An improper link resolution flaw can occur while extracting an archive leading to changing modes, times, access control lists, and flags of a file outside of the archive. An attacker may provide a malicious archive to a victim user, who would trigger this flaw when trying to extract the archive. A local attacker may use this flaw to gain more privileges in a system.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-31566
