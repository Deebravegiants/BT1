# [H] Apache Kylin Session Fixation vulnerability

## Summary
Severity: High
Advisory: GHSA-752q-72qc-rc66
CVE: CVE-2024-23590
CWE: CWE-384
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-11-04
Source: https://github.com/advisories/GHSA-752q-72qc-rc66
Type: github-advisory

## Affected
- Maven: `org.apache.kylin:kylin` — affected >=2.0.0 <5.0.0

## Details
Session Fixation vulnerability in Apache Kylin.

This issue affects Apache Kylin: from 2.0.0 through 4.x.

Users are recommended to upgrade to version 5.0.0 or above, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23590
- https://github.com/apache/kylin
- https://lists.apache.org/thread/7161154h0k6zygr9917qq0g95p39szml
- http://www.openwall.com/lists/oss-security/2024/11/03/1
