# [H] Apache Dolphin Scheduler has insufficiently protected credentials 

## Summary
Severity: High
Advisory: GHSA-jvc3-wjf6-7c6c
CVE: CVE-2022-26885
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-11-24
Source: https://github.com/advisories/GHSA-jvc3-wjf6-7c6c
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler-common` — affected >=0 <2.0.6

## Details
When using tasks to read config files, there is a risk of database password disclosure. We recommend you upgrade to version 2.0.6 or higher.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-26885
- https://github.com/apache/dolphinscheduler
- https://github.com/apache/dolphinscheduler/releases/tag/2.0.6
- https://lists.apache.org/thread/z7084r9cs2r26cszkkgjqpb5bhnxqssp
