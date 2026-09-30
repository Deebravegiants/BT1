# [C] Command injection in Apache DolphinScheduler Alert Plugins

## Summary
Severity: Critical
Advisory: GHSA-wqg7-mx6p-2rw3
CVE: CVE-2022-45462
CWE: CWE-77
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-23
Source: https://github.com/advisories/GHSA-wqg7-mx6p-2rw3
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler-alert-plugins` — affected >=0 <2.0.6

## Details
Alarm instance management has command injection when there is a specific command configured. It is only for logged-in users. We recommend you upgrade to version 2.0.6 or higher.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45462
- https://github.com/apache/dolphinscheduler/pull/10744
- https://github.com/apache/dolphinscheduler/pull/9834
- https://github.com/apache/dolphinscheduler
- https://lists.apache.org/thread/2f126y32bf1v3mvxkdgt2jr5j3l1t01w
- http://www.openwall.com/lists/oss-security/2022/11/23/1
