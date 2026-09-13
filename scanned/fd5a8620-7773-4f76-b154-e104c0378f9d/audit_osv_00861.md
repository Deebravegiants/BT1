# [H] ALPINE-CVE-2018-1000027

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-1000027
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1000027
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
- Alpine:v3.4: `squid` — affected >=0 <3.5.27-r0
- Alpine:v3.5: `squid` — affected >=0 <3.5.27-r0
- Alpine:v3.6: `squid` — affected >=0 <3.5.27-r0
- Alpine:v3.7: `squid` — affected >=0 <3.5.27-r0
- Alpine:v3.8: `squid` — affected >=0 <3.5.27-r2
- Alpine:v3.9: `squid` — affected >=0 <3.5.27-r2

## Details
The Squid Software Foundation Squid HTTP Caching Proxy version prior to version 4.0.23 contains a NULL Pointer Dereference vulnerability in HTTP Response X-Forwarded-For header processing that can result in Denial of Service to all clients of the proxy. This attack appear to be exploitable via Remote HTTP server responding with an X-Forwarded-For header to certain types of HTTP request. This vulnerability appears to have been fixed in 4.0.23 and later.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1000027
