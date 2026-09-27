# [H] ALPINE-CVE-2019-9517

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-9517
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-9517
Type: osv

## Affected
- Alpine:v3.10: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.11: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.12: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.13: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.7: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.8: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.9: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.10: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.11: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.12: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.13: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.14: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.15: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.16: `nodejs` — affected >=0 <10.16.3-r0

## Details
Some HTTP/2 implementations are vulnerable to unconstrained interal data buffering, potentially leading to a denial of service. The attacker opens the HTTP/2 window so the peer can send without constraint; however, they leave the TCP window closed so the peer cannot actually write (many of) the bytes on the wire. The attacker then sends a stream of requests for a large response object. Depending on how the servers queue the responses, this can consume excess memory, CPU, or both.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-9517
