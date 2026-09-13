# [M] ALPINE-CVE-2023-46846

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-46846
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-11-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-46846
Type: osv

## Affected
- Alpine:v3.19: `squid` — affected >=2.6 <6.4-r0
- Alpine:v3.20: `squid` — affected >=2.6 <6.4-r0
- Alpine:v3.21: `squid` — affected >=2.6 <6.4-r0
- Alpine:v3.22: `squid` — affected >=2.6 <6.4-r0
- Alpine:v3.23: `squid` — affected >=2.6 <6.4-r0
- Alpine:v3.24: `squid` — affected >=2.6 <6.4-r0

## Details
SQUID is vulnerable to HTTP request smuggling, caused by chunked decoder lenience, allows a remote attacker to perform Request/Response smuggling past firewall and frontend security systems.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-46846
