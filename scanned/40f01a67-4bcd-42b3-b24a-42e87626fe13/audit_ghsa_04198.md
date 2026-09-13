# [C] Apache DolphinScheduler: DataSource API Missing Authorization Check Leads to Arbitrary Data Source Metadata Disclosure 

## Summary
Severity: Critical
Advisory: GHSA-r989-cjhx-3v49
CVE: CVE-2026-32966
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-r989-cjhx-3v49
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler-api` — affected >=0 <3.4.2

## Details
DataSource API Missing Authorization Check Leads to Arbitrary Data Source Metadata Disclosure in Apache DolphinScheduler.

This issue affects Apache DolphinScheduler: before 3.4.2.

Users are recommended to upgrade to version 3.4.2, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-32966
- https://github.com/apache/dolphinscheduler
- https://lists.apache.org/thread/4f1fojpj26z9y5nd1ko845gcknpn75g2
- http://www.openwall.com/lists/oss-security/2026/06/17/2
