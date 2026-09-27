# [H] Apache HTTP Server: http2: double free and possible RCE on early reset

## Summary
Severity: High
Advisory: BIT-apache-2026-23918
Aliases: CVE-2026-23918
Ecosystem: Bitnami
Published: 2026-05-05
Source: https://osv.dev/vulnerability/BIT-apache-2026-23918
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.66 <2.4.67

## Details
Double Free and possible RCE vulnerability in Apache HTTP Server with the HTTP/2 protocol.

This issue affects Apache HTTP Server: 2.4.66.

Users are recommended to upgrade to version 2.4.67, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/05/04/19
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-23918
- https://access.redhat.com/errata/RHSA-2026:13938
- https://access.redhat.com/security/cve/CVE-2026-23918
- https://bugzilla.redhat.com/show_bug.cgi?id=2465304
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-23918.json
