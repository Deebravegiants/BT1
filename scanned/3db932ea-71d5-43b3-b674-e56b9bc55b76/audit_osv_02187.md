# [C] ALPINE-CVE-2021-29921

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-29921
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-29921
Type: osv

## Affected
- Alpine:v3.15: `python3` — affected >=0 <3.9.5-r0
- Alpine:v3.16: `python3` — affected >=0 <3.9.5-r0
- Alpine:v3.17: `python3` — affected >=0 <3.9.5-r0
- Alpine:v3.18: `python3` — affected >=0 <3.9.5-r0
- Alpine:v3.19: `python3` — affected >=0 <3.9.5-r0
- Alpine:v3.20: `python3` — affected >=0 <3.9.5-r0
- Alpine:v3.21: `python3` — affected >=0 <3.9.5-r0
- Alpine:v3.22: `python3` — affected >=0 <3.9.5-r0
- Alpine:v3.23: `python3` — affected >=0 <3.9.5-r0
- Alpine:v3.24: `python3` — affected >=0 <3.9.5-r0

## Details
In Python before 3,9,5, the ipaddress library mishandles leading zero characters in the octets of an IP address string. This (in some situations) allows attackers to bypass access control that is based on IP addresses.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-29921
