# [H] Apache HTTP Server: mod_proxy_html buffer overflow

## Summary
Severity: High
Advisory: BIT-apache-2026-34355
Aliases: CVE-2026-34355
Ecosystem: Bitnami
Published: 2026-06-10
Source: https://osv.dev/vulnerability/BIT-apache-2026-34355
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.68

## Details
A buffer overflow in mod_proxy_html in Apache HTTP Server 2.4.67 and earlier allows an attack by an untrusted backend.
Users are recommended to upgrade to version 2.4.68, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/08/6
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-34355
- https://access.redhat.com/errata/RHSA-2026:34109
- https://access.redhat.com/security/cve/CVE-2026-34355
- https://bugzilla.redhat.com/show_bug.cgi?id=2486414
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-34355.json
- https://access.redhat.com/errata/RHSA-2026:25042
- https://access.redhat.com/errata/RHSA-2026:41906
- https://access.redhat.com/errata/RHSA-2026:42828
- https://access.redhat.com/errata/RHSA-2026:47046
- https://access.redhat.com/errata/RHSA-2026:53371
- https://access.redhat.com/errata/RHSA-2026:56868
- https://access.redhat.com/errata/RHSA-2026:56869
- https://access.redhat.com/errata/RHSA-2026:62165
- https://access.redhat.com/errata/RHSA-2026:66323
