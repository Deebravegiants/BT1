# [M] Apache HTTP Server: source code disclosure with handlers configured via AddType

## Summary
Severity: Medium
Advisory: BIT-apache-2024-39884
Aliases: CVE-2024-39884
Ecosystem: Bitnami
Published: 2024-07-09
Source: https://osv.dev/vulnerability/BIT-apache-2024-39884
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.60 <2.4.61

## Details
A regression in the core of Apache HTTP Server 2.4.60 ignores some use of the legacy content-type based configuration of handlers.   "AddType" and similar configuration, under some circumstances where files are requested indirectly, result in source code disclosure of local content. For example, PHP scripts may be served instead of interpreted.

Users are recommended to upgrade to version 2.4.61, which fixes this issue.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://security.netapp.com/advisory/ntap-20240712-0002/
- http://www.openwall.com/lists/oss-security/2024/07/17/6
- http://www.openwall.com/lists/oss-security/2024/07/03/8
- https://nvd.nist.gov/vuln/detail/CVE-2024-39884
