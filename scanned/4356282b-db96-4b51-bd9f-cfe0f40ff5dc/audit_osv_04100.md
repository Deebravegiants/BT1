# [C] Apache HTTP Server: SSRF with mod_rewrite in server/vhost context on Windows

## Summary
Severity: Critical
Advisory: BIT-apache-2024-40898
Aliases: CVE-2024-40898
Ecosystem: Bitnami
Published: 2024-07-23
Source: https://osv.dev/vulnerability/BIT-apache-2024-40898
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.62

## Details
SSRF in Apache HTTP Server on Windows with mod_rewrite in server/vhost context, allows to potentially leak NTML hashes to a malicious server via SSRF and malicious requests.

Users are recommended to upgrade to version 2.4.62 which fixes this issue.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- http://www.openwall.com/lists/oss-security/2024/07/17/7
- https://security.netapp.com/advisory/ntap-20240808-0006/
- https://nvd.nist.gov/vuln/detail/CVE-2024-40898
