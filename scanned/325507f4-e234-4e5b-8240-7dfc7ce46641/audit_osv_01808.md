# [M] ALPINE-CVE-2020-15811

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-15811
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-09-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-15811
Type: osv

## Affected
- Alpine:v3.10: `squid` — affected >=5.0 <4.13-r0
- Alpine:v3.11: `squid` — affected >=5.0 <4.13-r0
- Alpine:v3.12: `squid` — affected >=5.0 <4.13-r0
- Alpine:v3.13: `squid` — affected >=5.0 <4.13.0-r0
- Alpine:v3.14: `squid` — affected >=5.0 <4.13.0-r0
- Alpine:v3.15: `squid` — affected >=5.0 <4.13.0-r0
- Alpine:v3.16: `squid` — affected >=5.0 <4.13.0-r0
- Alpine:v3.17: `squid` — affected >=5.0 <4.13.0-r0
- Alpine:v3.18: `squid` — affected >=5.0 <4.13.0-r0
- Alpine:v3.19: `squid` — affected >=5.0 <4.13.0-r0
- Alpine:v3.20: `squid` — affected >=5.0 <4.13.0-r0
- Alpine:v3.21: `squid` — affected >=5.0 <4.13.0-r0
- Alpine:v3.22: `squid` — affected >=5.0 <4.13.0-r0
- Alpine:v3.23: `squid` — affected >=5.0 <4.13.0-r0
- Alpine:v3.24: `squid` — affected >=5.0 <4.13.0-r0
- Alpine:v3.9: `squid` — affected >=5.0 <4.13-r0

## Details
An issue was discovered in Squid before 4.13 and 5.x before 5.0.4. Due to incorrect data validation, HTTP Request Splitting attacks may succeed against HTTP and HTTPS traffic. This leads to cache poisoning. This allows any client, including browser scripts, to bypass local security and poison the browser cache and any downstream caches with content from an arbitrary source. Squid uses a string search instead of parsing the Transfer-Encoding header to find chunked encoding. This allows an attacker to hide a second request inside Transfer-Encoding: it is interpreted by Squid as chunked and split out into a second request delivered upstream. Squid will then deliver two distinct responses to the client, corrupting any downstream caches.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-15811
