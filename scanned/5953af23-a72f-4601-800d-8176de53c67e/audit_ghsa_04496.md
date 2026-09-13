# [M] Apache DolphinScheduler: Incorrect Authorization vulnerability allows users to access workflow instance information belonging to projects they do not have permission to access. 

## Summary
Severity: Medium
Advisory: GHSA-wv7f-c794-82v6
CVE: CVE-2026-42357
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-wv7f-c794-82v6
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler-api` — affected >=0 <3.4.2

## Details
Incorrect Authorization vulnerability allows users to access workflow instance information belonging to projects they do not have permission to access.

This issue affects Apache DolphinScheduler versions prior to 3.4.2.


Users are recommended to upgrade to version 3.4.2, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42357
- https://github.com/apache/dolphinscheduler
- https://lists.apache.org/thread/74l2rrz32w2chn7vz64313gk7ox5wjtr
- http://www.openwall.com/lists/oss-security/2026/06/17/4
