# [M] ALPINE-CVE-2018-1050

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-1050
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 4.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2018-03-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1050
Type: osv

## Affected
- Alpine:v3.10: `samba` — affected >=3.6.0 <4.7.6-r0
- Alpine:v3.11: `samba` — affected >=3.6.0 <4.7.6-r0
- Alpine:v3.12: `samba` — affected >=3.6.0 <4.7.6-r0
- Alpine:v3.13: `samba` — affected >=3.6.0 <4.7.6-r0
- Alpine:v3.14: `samba` — affected >=3.6.0 <4.7.6-r0
- Alpine:v3.15: `samba` — affected >=3.6.0 <4.7.6-r0
- Alpine:v3.16: `samba` — affected >=3.6.0 <4.7.6-r0
- Alpine:v3.17: `samba` — affected >=3.6.0 <4.7.6-r0
- Alpine:v3.18: `samba` — affected >=3.6.0 <4.7.6-r0
- Alpine:v3.19: `samba` — affected >=3.6.0 <4.7.6-r0
- Alpine:v3.20: `samba` — affected >=3.6.0 <4.7.6-r0
- Alpine:v3.21: `samba` — affected >=3.6.0 <4.7.6-r0
- Alpine:v3.22: `samba` — affected >=3.6.0 <4.7.6-r0
- Alpine:v3.23: `samba` — affected >=3.6.0 <4.7.6-r0
- Alpine:v3.24: `samba` — affected >=3.6.0 <4.7.6-r0
- Alpine:v3.4: `samba` — affected >=3.6.0 <4.4.16-r2
- Alpine:v3.5: `samba` — affected >=3.6.0 <4.5.16-r0
- Alpine:v3.6: `samba` — affected >=3.6.0 <4.6.14-r0
- Alpine:v3.7: `samba` — affected >=3.6.0 <4.7.6-r0
- Alpine:v3.8: `samba` — affected >=3.6.0 <4.7.6-r0
- Alpine:v3.9: `samba` — affected >=3.6.0 <4.7.6-r0

## Details
All versions of Samba from 4.0.0 onwards are vulnerable to a denial of service attack when the RPC spoolss service is configured to be run as an external daemon. Missing input sanitization checks on some of the input parameters to spoolss RPC calls could cause the print spooler service to crash.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1050
