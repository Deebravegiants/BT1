# [C] Apache HTTP Server: mod_ssl access control bypass with session resumption

## Summary
Severity: Critical
Advisory: BIT-apache-2025-23048
Aliases: CVE-2025-23048
Ecosystem: Bitnami
Published: 2025-07-16
Source: https://osv.dev/vulnerability/BIT-apache-2025-23048
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.35 <2.4.64

## Details
In some mod_ssl configurations on Apache HTTP Server 2.4.35 through to 2.4.63, an access control bypass by trusted clients is possible using TLS 1.3 session resumption.

Configurations are affected when mod_ssl is configured for multiple virtual hosts, with each restricted to a different set of trusted client certificates (for example with a different SSLCACertificateFile/Path setting). In such a case, a client trusted to access one virtual host may be able to access another virtual host, if SSLStrictSNIVHostCheck is not enabled in either virtual host.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-23048
- http://www.openwall.com/lists/oss-security/2025/07/10/2
- http://www.openwall.com/lists/oss-security/2025/07/10/8
- https://lists.debian.org/debian-lts-announce/2025/08/msg00009.html
