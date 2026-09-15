# [M] ALPINE-CVE-2019-14847

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-14847
Ecosystem: Alpine:v3.10, Alpine:v3.8, Alpine:v3.9
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-14847
Type: osv

## Affected
- Alpine:v3.10: `samba` — affected >=4.0.0 <4.10.10-r0
- Alpine:v3.8: `samba` — affected >=4.0.0 <4.8.12-r1
- Alpine:v3.9: `samba` — affected >=4.0.0 <4.8.12-r1

## Details
A flaw was found in samba 4.0.0 before samba 4.9.15 and samba 4.10.x before 4.10.10. An attacker can crash AD DC LDAP server via dirsync resulting in denial of service. Privilege escalation is not possible with this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-14847
