# [H] CVE-2019-1000022

## Summary
Severity: High
Advisory: CVE-2019-1000022
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-04
Source: https://osv.dev/vulnerability/CVE-2019-1000022
Type: osv

## Details
Taoensso Sente version Prior to version 1.14.0 contains a Cross Site Request Forgery (CSRF) vulnerability in WebSocket handshake endpoint that can result in CSRF attack, possible leak of anti-CSRF token. This attack appears to be exploitable via malicious request against WebSocket handshake endpoint. This vulnerability appears to have been fixed in 1.14.0 and later.

## References
- https://github.com/ptaoussanis/sente/issues/137
