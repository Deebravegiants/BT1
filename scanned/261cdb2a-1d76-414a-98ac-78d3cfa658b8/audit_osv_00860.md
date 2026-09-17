# [H] ALPINE-CVE-2018-1000024

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-1000024
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1000024
Type: osv

## Affected
- Alpine:v3.10: `squid` — affected >=3.0 <3.5.27-r2
- Alpine:v3.11: `squid` — affected >=3.0 <3.5.27-r2
- Alpine:v3.12: `squid` — affected >=3.0 <3.5.27-r2
- Alpine:v3.13: `squid` — affected >=3.0 <3.5.27-r2
- Alpine:v3.14: `squid` — affected >=3.0 <3.5.27-r2
- Alpine:v3.15: `squid` — affected >=3.0 <3.5.27-r2
- Alpine:v3.16: `squid` — affected >=3.0 <3.5.27-r2
- Alpine:v3.17: `squid` — affected >=3.0 <3.5.27-r2
- Alpine:v3.18: `squid` — affected >=3.0 <3.5.27-r2
- Alpine:v3.19: `squid` — affected >=3.0 <3.5.27-r2
- Alpine:v3.20: `squid` — affected >=3.0 <3.5.27-r2
- Alpine:v3.21: `squid` — affected >=3.0 <3.5.27-r2
- Alpine:v3.22: `squid` — affected >=3.0 <3.5.27-r2
- Alpine:v3.23: `squid` — affected >=3.0 <3.5.27-r2
- Alpine:v3.24: `squid` — affected >=3.0 <3.5.27-r2
- Alpine:v3.4: `squid` — affected >=3.0 <3.5.27-r0
- Alpine:v3.5: `squid` — affected >=3.0 <3.5.27-r0
- Alpine:v3.6: `squid` — affected >=3.0 <3.5.27-r0
- Alpine:v3.7: `squid` — affected >=3.0 <3.5.27-r0
- Alpine:v3.8: `squid` — affected >=3.0 <3.5.27-r2
- Alpine:v3.9: `squid` — affected >=3.0 <3.5.27-r2

## Details
The Squid Software Foundation Squid HTTP Caching Proxy version 3.0 to 3.5.27, 4.0 to 4.0.22 contains a Incorrect Pointer Handling vulnerability in ESI Response Processing that can result in Denial of Service for all clients using the proxy.. This attack appear to be exploitable via Remote server delivers an HTTP response payload containing valid but unusual ESI syntax.. This vulnerability appears to have been fixed in 4.0.23 and later.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1000024
