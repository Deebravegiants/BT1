# [M] ALPINE-CVE-2023-0225

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-0225
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-04-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-0225
Type: osv

## Affected
- Alpine:v3.18: `samba` — affected >=4.17.0 <4.18.1-r0
- Alpine:v3.19: `samba` — affected >=4.17.0 <4.18.1-r0
- Alpine:v3.20: `samba` — affected >=4.17.0 <4.18.1-r0
- Alpine:v3.21: `samba` — affected >=4.17.0 <4.18.1-r0
- Alpine:v3.22: `samba` — affected >=4.17.0 <4.18.1-r0
- Alpine:v3.23: `samba` — affected >=4.17.0 <4.18.1-r0
- Alpine:v3.24: `samba` — affected >=4.17.0 <4.18.1-r0

## Details
A flaw was found in Samba. An incomplete access check on dnsHostName allows authenticated but otherwise unprivileged users to delete this attribute from any object in the directory.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-0225
