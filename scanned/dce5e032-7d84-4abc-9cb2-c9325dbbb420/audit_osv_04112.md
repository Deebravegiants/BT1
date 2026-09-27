# [M] Apache HTTP Server: CGI environment variable override

## Summary
Severity: Medium
Advisory: BIT-apache-2025-65082
Aliases: CVE-2025-65082
Ecosystem: Bitnami
Published: 2025-12-09
Source: https://osv.dev/vulnerability/BIT-apache-2025-65082
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.66

## Details
Improper Neutralization of Escape, Meta, or Control Sequences vulnerability in Apache HTTP Server through environment variables set via the Apache configuration unexpectedly superseding variables calculated by the server for CGI programs.

This issue affects Apache HTTP Server from 2.4.0 through 2.4.65.

Users are recommended to upgrade to version 2.4.66 which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/12/04/7
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-65082
