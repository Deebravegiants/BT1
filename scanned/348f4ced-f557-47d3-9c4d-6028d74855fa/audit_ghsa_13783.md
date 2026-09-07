# [M] Apache DolphinScheduler Missing Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r44q-98gx-pmh2
CVE: CVE-2023-49620
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-11-30
Source: https://github.com/advisories/GHSA-r44q-98gx-pmh2
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler-api` — affected >=0 <3.1.0
- Maven: `org.apache.dolphinscheduler:dolphinscheduler-common` — affected >=0 <3.1.0
- Maven: `org.apache.dolphinscheduler:dolphinscheduler-dao` — affected >=0 <3.1.0
- Maven: `org.apache.dolphinscheduler:dolphinscheduler-service` — affected >=0 <3.1.0

## Details
Before DolphinScheduler version 3.1.0, the login user could delete UDF function in the resource center unauthorized (which almost used in sql task), with unauthorized access vulnerability (IDOR), but after version 3.1.0 we fixed this issue. We mark this cve as moderate level because it still requires user login to operate, please upgrade to version 3.1.0 to avoid this vulnerability

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49620
- https://github.com/apache/dolphinscheduler/pull/10307
- https://github.com/apache/dolphinscheduler/commit/a4948f58e671ab263060da1de255af3ecd2530ac
- https://github.com/apache/dolphinscheduler
- https://lists.apache.org/thread/zm4t1ykj4cro1c8183q7y32z0yzfz8yj
- http://www.openwall.com/lists/oss-security/2023/11/30/4
