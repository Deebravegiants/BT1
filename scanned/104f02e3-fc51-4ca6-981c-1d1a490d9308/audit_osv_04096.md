# [C] Apache HTTP Server may use exploitable/malicious backend application output to run local handlers via internal redirect

## Summary
Severity: Critical
Advisory: BIT-apache-2024-38476
Aliases: CVE-2024-38476
Ecosystem: Bitnami
Published: 2024-07-03
Source: https://osv.dev/vulnerability/BIT-apache-2024-38476
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.60

## Details
Vulnerability in core of Apache HTTP Server 2.4.59 and earlier are vulnerably to information disclosure, SSRF or local script execution via backend applications whose response headers are malicious or exploitable.

Users are recommended to upgrade to version 2.4.60, which fixes this issue.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://security.netapp.com/advisory/ntap-20240712-0001/
- http://www.openwall.com/lists/oss-security/2024/07/01/9
- https://nvd.nist.gov/vuln/detail/CVE-2024-38476
- http://seclists.org/fulldisclosure/2024/Oct/11
