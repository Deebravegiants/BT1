# [H] Apache HTTP Server: Stack Buffer Over-Read in mod_ssl OCSP `send_request`

## Summary
Severity: High
Advisory: BIT-apache-2026-44185
Aliases: CVE-2026-44185
Ecosystem: Bitnami
Published: 2026-06-10
Source: https://osv.dev/vulnerability/BIT-apache-2026-44185
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.68

## Details
Buffer Over-read vulnerability in Apache HTTP Server via outbound OCSP requests to an attacker controlled OCSP server

This issue affects Apache HTTP Server: from 2.4.0 through 2.4.67.

Users are recommended to upgrade to version 2.4.68, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/08/12
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-44185
- https://access.redhat.com/errata/RHSA-2026:34109
- https://access.redhat.com/security/cve/CVE-2026-44185
- https://bugzilla.redhat.com/show_bug.cgi?id=2486397
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-44185.json
- https://access.redhat.com/errata/RHSA-2026:25042
- https://access.redhat.com/errata/RHSA-2026:41906
- https://access.redhat.com/errata/RHSA-2026:42828
- https://access.redhat.com/errata/RHSA-2026:47046
- https://access.redhat.com/errata/RHSA-2026:53371
- https://access.redhat.com/errata/RHSA-2026:56868
- https://access.redhat.com/errata/RHSA-2026:56869
- https://access.redhat.com/errata/RHSA-2026:62165
- https://access.redhat.com/errata/RHSA-2026:66323
