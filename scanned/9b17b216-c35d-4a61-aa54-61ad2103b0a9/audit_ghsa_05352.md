# [M] Apache DolphinScheduler: Incorrect Authorization vulnerability allows users with system login privileges to delete task definitions in unauthorized projects

## Summary
Severity: Medium
Advisory: GHSA-wh3w-v6gj-fqh2
CVE: CVE-2026-41280
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-wh3w-v6gj-fqh2
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler-api` — affected >=0 <3.4.2

## Details
Incorrect Authorization vulnerability allows users with system login privileges to delete task definitions in unauthorized projects

This issue affects Apache DolphinScheduler versions prior to 3.4.2. 

Users are recommended to upgrade to version 3.4.2, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41280
- https://github.com/apache/dolphinscheduler
- https://lists.apache.org/thread/5bv1njp3lbbbj11y20td5yz1b4nmrtvw
- http://www.openwall.com/lists/oss-security/2026/06/17/7
