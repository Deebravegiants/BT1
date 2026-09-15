# [C] Apache Syncope: SQL injection vulnerability in Audit Events search

## Summary
Severity: Critical
Advisory: CVE-2026-57308
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-57308
Type: osv

## Details
Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection') vulnerability in Apache Syncope.

An administrator with adequate entitlements can achieve execution of arbitrary SQL via stacked queries, leveraging unsanitized sort parameters.

This issue affects Apache Syncope: from 3.0.0-M0 through 3.0.16, from 4.0.0-M0 Through 4.0.6, from 4.1.0-M0 through 4.1.1.


Users are recommended to upgrade to version 4.0.7 / 4.1.2, which fix this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/20/8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57308.json
- https://lists.apache.org/thread/g0gpctj90pbczbjl5jr33t8gr1gltg8v
- https://nvd.nist.gov/vuln/detail/CVE-2026-57308
