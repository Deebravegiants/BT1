# [M] Apache HTTP Server: DoS by Null pointer in websocket over HTTP/2

## Summary
Severity: Medium
Advisory: BIT-apache-2024-36387
Aliases: CVE-2024-36387
Ecosystem: Bitnami
Published: 2024-07-03
Source: https://osv.dev/vulnerability/BIT-apache-2024-36387
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.55 <2.4.60

## Details
Serving WebSocket protocol upgrades over a HTTP/2 connection could result in a Null Pointer dereference, leading to a crash of the server process, degrading performance.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://security.netapp.com/advisory/ntap-20240712-0001/
- http://www.openwall.com/lists/oss-security/2024/07/01/4
- https://nvd.nist.gov/vuln/detail/CVE-2024-36387
