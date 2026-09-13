# [H] Apache HTTP Server proxy encoding problem

## Summary
Severity: High
Advisory: BIT-apache-2024-38473
Aliases: CVE-2024-38473
Ecosystem: Bitnami
Published: 2024-07-03
Source: https://osv.dev/vulnerability/BIT-apache-2024-38473
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.60

## Details
Encoding problem in mod_proxy in Apache HTTP Server 2.4.59 and earlier allows request URLs with incorrect encoding to be sent to backend services, potentially bypassing authentication via crafted requests.
Users are recommended to upgrade to version 2.4.60, which fixes this issue.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://security.netapp.com/advisory/ntap-20240712-0001/
- http://www.openwall.com/lists/oss-security/2024/07/01/6
- https://nvd.nist.gov/vuln/detail/CVE-2024-38473
