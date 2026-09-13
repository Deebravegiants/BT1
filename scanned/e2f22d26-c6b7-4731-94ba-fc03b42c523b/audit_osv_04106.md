# [H] Apache HTTP Server: mod_proxy_http2 denial of service

## Summary
Severity: High
Advisory: BIT-apache-2025-49630
Aliases: CVE-2025-49630
Ecosystem: Bitnami
Published: 2025-07-16
Source: https://osv.dev/vulnerability/BIT-apache-2025-49630
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.26 <2.4.64

## Details
In certain proxy configurations, a denial of service attack against Apache HTTP Server versions 2.4.26 through to 2.4.63 can be triggered by untrusted clients causing an assertion in mod_proxy_http2.

Configurations affected are a reverse proxy is configured for an HTTP/2 backend, with ProxyPreserveHost set to "on".

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-49630
- http://www.openwall.com/lists/oss-security/2025/07/10/2
- http://www.openwall.com/lists/oss-security/2025/07/10/7
- https://lists.debian.org/debian-lts-announce/2025/08/msg00009.html
