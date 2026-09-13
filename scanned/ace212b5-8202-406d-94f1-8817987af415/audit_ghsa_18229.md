# [H] Apache DolphinScheduler vulnerable to Alert Script Attack

## Summary
Severity: High
Advisory: GHSA-3vcp-r62v-xpvg
CVE: CVE-2024-43115
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-3vcp-r62v-xpvg
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler` — affected >=0 <3.2.2

## Details
Improper Input Validation vulnerability in Apache DolphinScheduler. An authenticated user can execute any shell script server by alert script.


This issue affects Apache DolphinScheduler: before 3.2.2.

Users are recommended to upgrade to version 3.3.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-43115
- https://github.com/apache/dolphinscheduler
- https://lists.apache.org/thread/qm36nrsv1vrr2j4o5q2wo75h3686hrnj
- http://www.openwall.com/lists/oss-security/2025/09/03/1
