# [H] Apache HTTP Server: mod_ssl TLS upgrade attack

## Summary
Severity: High
Advisory: BIT-apache-2025-49812
Aliases: CVE-2025-49812
Ecosystem: Bitnami
Published: 2025-07-16
Source: https://osv.dev/vulnerability/BIT-apache-2025-49812
Type: osv

## Affected
- Bitnami: `apache` — affected >=0 <2.4.64

## Details
In some mod_ssl configurations on Apache HTTP Server versions through to 2.4.63, an HTTP desynchronisation attack allows a man-in-the-middle attacker to hijack an HTTP session via a TLS upgrade.

Only configurations using "SSLEngine optional" to enable TLS upgrades are affected. Users are recommended to upgrade to version 2.4.64, which removes support for TLS upgrade.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-49812
- http://www.openwall.com/lists/oss-security/2025/07/09/3
- http://www.openwall.com/lists/oss-security/2025/07/10/2
- http://www.openwall.com/lists/oss-security/2025/07/10/9
- https://lists.debian.org/debian-lts-announce/2025/08/msg00009.html
