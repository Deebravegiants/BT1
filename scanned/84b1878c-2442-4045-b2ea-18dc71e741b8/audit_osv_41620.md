# [H] Apache Kylin: OS Command Injection via Async Query API

## Summary
Severity: High
Advisory: CVE-2026-62392
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-62392
Type: osv

## Details
Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection') vulnerability in Apache Kylin. A backend API may bring job config parameters to OS command line.

This issue affects Apache Kylin: from 4 through 5.0.3.

Users are recommended to upgrade to version 5.0.4, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/14/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62392.json
- https://lists.apache.org/thread/9hof8lxo3mzshsh5r77mskzqlkns09gn
- https://nvd.nist.gov/vuln/detail/CVE-2026-62392
