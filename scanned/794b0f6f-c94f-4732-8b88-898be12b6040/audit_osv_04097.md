# [H] Apache HTTP Server: Crash resulting in Denial of Service in mod_proxy via a malicious request

## Summary
Severity: High
Advisory: BIT-apache-2024-38477
Aliases: CVE-2024-38477
Ecosystem: Bitnami
Published: 2024-07-03
Source: https://osv.dev/vulnerability/BIT-apache-2024-38477
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.60

## Details
null pointer dereference in mod_proxy in Apache HTTP Server 2.4.59 and earlier allows an attacker to crash the server via a malicious request.
Users are recommended to upgrade to version 2.4.60, which fixes this issue.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://security.netapp.com/advisory/ntap-20240712-0001/
- http://www.openwall.com/lists/oss-security/2024/07/01/10
- https://nvd.nist.gov/vuln/detail/CVE-2024-38477
- http://seclists.org/fulldisclosure/2024/Oct/11
