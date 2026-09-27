# [H] Apache HTTP Server: mod_md (ACME), unintended retry intervals

## Summary
Severity: High
Advisory: BIT-apache-2025-55753
Aliases: CVE-2025-55753
Ecosystem: Bitnami
Published: 2025-12-09
Source: https://osv.dev/vulnerability/BIT-apache-2025-55753
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.30 <2.4.66

## Details
An integer overflow in the case of failed ACME certificate renewal leads, after a number of failures (~30 days in default configurations), to the backoff timer becoming 0. Attempts to renew the certificate then are repeated without delays until it succeeds.

This issue affects Apache HTTP Server: from 2.4.30 before 2.4.66.


Users are recommended to upgrade to version 2.4.66, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/12/04/4
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-55753
