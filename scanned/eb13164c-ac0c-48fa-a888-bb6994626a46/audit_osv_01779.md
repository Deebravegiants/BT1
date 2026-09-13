# [M] ALPINE-CVE-2020-14383

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-14383
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14383
Type: osv

## Affected
- Alpine:v3.11: `samba` — affected >=4.0.0 <4.11.16-r0
- Alpine:v3.12: `samba` — affected >=4.0.0 <4.12.9-r0
- Alpine:v3.13: `samba` — affected >=4.0.0 <4.12.9-r0
- Alpine:v3.14: `samba` — affected >=4.0.0 <4.12.9-r0
- Alpine:v3.15: `samba` — affected >=4.0.0 <4.12.9-r0
- Alpine:v3.16: `samba` — affected >=4.0.0 <4.12.9-r0
- Alpine:v3.17: `samba` — affected >=4.0.0 <4.12.9-r0
- Alpine:v3.18: `samba` — affected >=4.0.0 <4.12.9-r0
- Alpine:v3.19: `samba` — affected >=4.0.0 <4.12.9-r0
- Alpine:v3.20: `samba` — affected >=4.0.0 <4.12.9-r0
- Alpine:v3.21: `samba` — affected >=4.0.0 <4.12.9-r0
- Alpine:v3.22: `samba` — affected >=4.0.0 <4.12.9-r0
- Alpine:v3.23: `samba` — affected >=4.0.0 <4.12.9-r0
- Alpine:v3.24: `samba` — affected >=4.0.0 <4.12.9-r0

## Details
A flaw was found in samba's DNS server. An authenticated user could use this flaw to the RPC server to crash. This RPC server, which also serves protocols other than dnsserver, will be restarted after a short delay, but it is easy for an authenticated non administrative attacker to crash it again as soon as it returns. The Samba DNS server itself will continue to operate, but many RPC services will not.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14383
