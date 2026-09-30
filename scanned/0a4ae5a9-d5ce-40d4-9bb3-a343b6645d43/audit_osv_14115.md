# [M] CVE-2018-7287

## Summary
Severity: Medium
Advisory: CVE-2018-7287
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-22
Source: https://osv.dev/vulnerability/CVE-2018-7287
Type: osv

## Details
An issue was discovered in res_http_websocket.c in Asterisk 15.x through 15.2.1. If the HTTP server is enabled (default is disabled), WebSocket payloads of size 0 are mishandled (with a busy loop).

## References
- http://downloads.digium.com/pub/security/AST-2018-006.html
- http://www.securityfocus.com/bid/103120
- http://www.securitytracker.com/id/1040419
- https://issues.asterisk.org/jira/browse/ASTERISK-27658
