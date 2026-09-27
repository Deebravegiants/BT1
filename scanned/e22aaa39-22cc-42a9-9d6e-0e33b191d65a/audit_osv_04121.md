# [M] Apache HTTP Server: mod_auth_digest timing attack

## Summary
Severity: Medium
Advisory: BIT-apache-2026-33006
Aliases: CVE-2026-33006
Ecosystem: Bitnami
Published: 2026-05-05
Source: https://osv.dev/vulnerability/BIT-apache-2026-33006
Type: osv

## Affected
- Bitnami: `apache` — affected >=0 <2.4.67

## Details
A timing attack against mod_auth_digest in Apache HTTP Server 2.4.66 allows a bypass of Digest authentication by a remote attacker.

Users are recommended to upgrade to version 2.4.67, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/05/04/21
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-33006
