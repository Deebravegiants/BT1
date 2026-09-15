# [M] ALPINE-CVE-2019-14907

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-14907
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-01-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-14907
Type: osv

## Affected
- Alpine:v3.10: `samba` — affected >=4.9.0 <4.10.12-r0
- Alpine:v3.11: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.12: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.13: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.14: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.15: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.16: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.17: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.18: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.19: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.20: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.21: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.22: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.23: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.24: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.8: `samba` — affected >=4.9.0 <4.8.12-r2
- Alpine:v3.9: `samba` — affected >=4.9.0 <4.8.12-r2

## Details
All samba versions 4.9.x before 4.9.18, 4.10.x before 4.10.12 and 4.11.x before 4.11.5 have an issue where if it is set with "log level = 3" (or above) then the string obtained from the client, after a failed character conversion, is printed. Such strings can be provided during the NTLMSSP authentication exchange. In the Samba AD DC in particular, this may cause a long-lived process(such as the RPC server) to terminate. (In the file server case, the most likely target, smbd, operates as process-per-client and so a crash there is harmless).

## References
- https://security.alpinelinux.org/vuln/CVE-2019-14907
