# [M] ALPINE-CVE-2018-1172

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-1172
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1172
Type: osv

## Affected
- Alpine:v3.10: `squid` — affected >=0 <3.5.27-r2
- Alpine:v3.11: `squid` — affected >=0 <3.5.27-r2
- Alpine:v3.12: `squid` — affected >=0 <3.5.27-r2
- Alpine:v3.13: `squid` — affected >=0 <3.5.27-r2
- Alpine:v3.14: `squid` — affected >=0 <3.5.27-r2
- Alpine:v3.15: `squid` — affected >=0 <3.5.27-r2
- Alpine:v3.16: `squid` — affected >=0 <3.5.27-r2
- Alpine:v3.17: `squid` — affected >=0 <3.5.27-r2
- Alpine:v3.18: `squid` — affected >=0 <3.5.27-r2
- Alpine:v3.19: `squid` — affected >=0 <3.5.27-r2
- Alpine:v3.20: `squid` — affected >=0 <3.5.27-r2
- Alpine:v3.21: `squid` — affected >=0 <3.5.27-r2
- Alpine:v3.22: `squid` — affected >=0 <3.5.27-r2
- Alpine:v3.23: `squid` — affected >=0 <3.5.27-r2
- Alpine:v3.24: `squid` — affected >=0 <3.5.27-r2
- Alpine:v3.8: `squid` — affected >=0 <3.5.27-r2
- Alpine:v3.9: `squid` — affected >=0 <3.5.27-r2

## Details
This vulnerability allows remote attackers to deny service on vulnerable installations of The Squid Software Foundation Squid 3.5.27-20180318. Authentication is not required to exploit this vulnerability. The specific flaw exists within ClientRequestContext::sslBumpAccessCheck(). A crafted request can trigger the dereference of a null pointer. An attacker can leverage this vulnerability to create a denial-of-service condition to users of the system. Was ZDI-CAN-6088.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1172
