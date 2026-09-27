# [M] ALPINE-CVE-2023-42670

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-42670
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-42670
Type: osv

## Affected
- Alpine:v3.18: `samba` — affected >=4.18.0 <4.18.8-r0
- Alpine:v3.19: `samba` — affected >=4.18.0 <4.18.8-r0
- Alpine:v3.20: `samba` — affected >=4.18.0 <4.18.8-r0
- Alpine:v3.21: `samba` — affected >=4.18.0 <4.18.8-r0
- Alpine:v3.22: `samba` — affected >=4.18.0 <4.18.8-r0
- Alpine:v3.23: `samba` — affected >=4.18.0 <4.18.8-r0
- Alpine:v3.24: `samba` — affected >=4.18.0 <4.18.8-r0

## Details
A flaw was found in Samba. It is susceptible to a vulnerability where multiple incompatible RPC listeners can be initiated, causing disruptions in the AD DC service. When Samba's RPC server experiences a high load or unresponsiveness, servers intended for non-AD DC purposes (for example, NT4-emulation "classic DCs") can erroneously start and compete for the same unix domain sockets. This issue leads to partial query responses from the AD DC, causing issues such as "The procedure number is out of range" when using tools like Active Directory Users. This flaw allows an attacker to disrupt AD DC services.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-42670
