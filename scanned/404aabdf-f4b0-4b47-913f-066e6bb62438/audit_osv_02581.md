# [H] ALPINE-CVE-2022-32743

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-32743
Ecosystem: Alpine:v3.14, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-09-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-32743
Type: osv

## Affected
- Alpine:v3.14: `samba` — affected >=4.1.0 <4.14.14-r0
- Alpine:v3.18: `samba` — affected >=4.1.0 <4.17.0-r0
- Alpine:v3.19: `samba` — affected >=4.1.0 <4.17.0-r0
- Alpine:v3.20: `samba` — affected >=4.1.0 <4.17.0-r0
- Alpine:v3.21: `samba` — affected >=4.1.0 <4.17.0-r0
- Alpine:v3.22: `samba` — affected >=4.1.0 <4.17.0-r0
- Alpine:v3.23: `samba` — affected >=4.1.0 <4.17.0-r0
- Alpine:v3.24: `samba` — affected >=4.1.0 <4.17.0-r0

## Details
Samba does not validate the Validated-DNS-Host-Name right for the dNSHostName attribute which could permit unprivileged users to write it.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-32743
