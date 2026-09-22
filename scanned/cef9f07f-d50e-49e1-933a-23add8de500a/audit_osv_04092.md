# [H] BIT-apache-2024-38472

## Summary
Severity: High
Advisory: BIT-apache-2024-38472
Aliases: CVE-2024-38472
Ecosystem: Bitnami
Published: 2024-07-03
Source: https://osv.dev/vulnerability/BIT-apache-2024-38472
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.60

## Details
SSRF in Apache HTTP Server on Windows allows to potentially leak NTML hashes to a malicious server via SSRF and malicious requests or content Users are recommended to upgrade to version 2.4.60 which fixes this issue.  Note: Existing configurations that access UNC paths will have to configure new directive "UNCList" to allow access during request processing.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://security.netapp.com/advisory/ntap-20240712-0001/
