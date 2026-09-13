# [H] ALPINE-CVE-2021-3618

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-3618
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-03-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3618
Type: osv

## Affected
- Alpine:v3.14: `nginx` — affected >=0 <1.20.1-r1
- Alpine:v3.15: `nginx` — affected >=0 <1.20.1-r1
- Alpine:v3.16: `nginx` — affected >=0 <1.20.1-r1
- Alpine:v3.17: `nginx` — affected >=0 <1.20.1-r1
- Alpine:v3.18: `nginx` — affected >=0 <1.20.1-r1
- Alpine:v3.19: `nginx` — affected >=0 <1.20.1-r1
- Alpine:v3.20: `nginx` — affected >=0 <1.20.1-r1
- Alpine:v3.21: `nginx` — affected >=0 <1.20.1-r1
- Alpine:v3.22: `nginx` — affected >=0 <1.20.1-r1
- Alpine:v3.23: `nginx` — affected >=0 <1.20.1-r1
- Alpine:v3.24: `nginx` — affected >=0 <1.20.1-r1

## Details
ALPACA is an application layer protocol content confusion attack, exploiting TLS servers implementing different protocols but using compatible certificates, such as multi-domain or wildcard certificates. A MiTM attacker having access to victim's traffic at the TCP/IP layer can redirect traffic from one subdomain to another, resulting in a valid TLS session. This breaks the authentication of TLS and cross-protocol attacks may be possible where the behavior of one protocol service may compromise the other at the application layer.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3618
