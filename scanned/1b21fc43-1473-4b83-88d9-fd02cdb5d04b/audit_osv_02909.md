# [H] ALPINE-CVE-2023-46847

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-46847
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-46847
Type: osv

## Affected
- Alpine:v3.19: `squid` — affected >=3.2.0.1 <6.4-r0
- Alpine:v3.20: `squid` — affected >=3.2.0.1 <6.4-r0
- Alpine:v3.21: `squid` — affected >=3.2.0.1 <6.4-r0
- Alpine:v3.22: `squid` — affected >=3.2.0.1 <6.4-r0
- Alpine:v3.23: `squid` — affected >=3.2.0.1 <6.4-r0
- Alpine:v3.24: `squid` — affected >=3.2.0.1 <6.4-r0

## Details
Squid is vulnerable to a Denial of Service,  where a remote attacker can perform buffer overflow attack by writing up to 2 MB of arbitrary data to heap memory when Squid is configured to accept HTTP Digest Authentication.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-46847
