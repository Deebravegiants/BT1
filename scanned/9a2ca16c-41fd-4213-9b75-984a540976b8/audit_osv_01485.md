# [M] ALPINE-CVE-2019-16935

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-16935
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-09-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-16935
Type: osv

## Affected
- Alpine:v3.11: `python2` — affected >=0 <2.7.16-r3
- Alpine:v3.12: `python2` — affected >=0 <2.7.16-r3
- Alpine:v3.10: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.11: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.12: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.13: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.14: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.15: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.16: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.17: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.18: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.19: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.20: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.21: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.22: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.23: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.24: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.7: `python3` — affected >=0 <3.6.9-r1
- Alpine:v3.8: `python3` — affected >=0 <3.6.9-r1
- Alpine:v3.9: `python3` — affected >=0 <3.6.9-r2

## Details
The documentation XML-RPC server in Python through 2.7.16, 3.x through 3.6.9, and 3.7.x through 3.7.4 has XSS via the server_title field. This occurs in Lib/DocXMLRPCServer.py in Python 2.x, and in Lib/xmlrpc/server.py in Python 3.x. If set_server_title is called with untrusted input, arbitrary JavaScript can be delivered to clients that visit the http URL for this server.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-16935
