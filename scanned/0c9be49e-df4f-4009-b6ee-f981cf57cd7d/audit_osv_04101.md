# [H] Apache HTTP Server: SSRF with mod_headers setting Content-Type header

## Summary
Severity: High
Advisory: BIT-apache-2024-43204
Aliases: CVE-2024-43204
Ecosystem: Bitnami
Published: 2025-07-16
Source: https://osv.dev/vulnerability/BIT-apache-2024-43204
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.64

## Details
SSRF in Apache HTTP Server with mod_proxy loaded allows an attacker to send outbound proxy requests to a URL controlled by the attacker.  Requires an unlikely configuration where mod_headers is configured to modify the Content-Type request or response header with a value provided in the HTTP request.

Users are recommended to upgrade to version 2.4.64 which fixes this issue.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-43204
- http://www.openwall.com/lists/oss-security/2025/07/10/2
- http://www.openwall.com/lists/oss-security/2025/07/10/4
- https://lists.debian.org/debian-lts-announce/2025/08/msg00009.html
