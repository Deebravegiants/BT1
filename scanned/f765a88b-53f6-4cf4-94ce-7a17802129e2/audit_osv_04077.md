# [M] read beyond bounds in mod_isapi

## Summary
Severity: Medium
Advisory: BIT-apache-2022-28330
Aliases: CVE-2022-28330
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apache-2022-28330
Type: osv

## Affected
- Bitnami: `apache` — affected >=0 <2.4.54

## Details
Apache HTTP Server 2.4.53 and earlier on Windows may read beyond bounds when configured to process requests with the mod_isapi module.

## References
- http://www.openwall.com/lists/oss-security/2022/06/08/3
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://security.netapp.com/advisory/ntap-20220624-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2022-28330
