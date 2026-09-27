# [H] Apache Geode OQL method invocation vulnerability

## Summary
Severity: High
Advisory: GHSA-6m68-3w55-6mx4
CVE: CVE-2017-9795
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-6m68-3w55-6mx4
Type: github-advisory

## Affected
- Maven: `org.apache.geode:geode-core` — affected >=1.0.0 <1.3.0

## Details
When an Apache Geode cluster before v1.3.0 is operating in secure mode, a user with read access to specific regions within a Geode cluster may execute OQL queries that allow read and write access to objects within unauthorized regions. In addition a user could invoke methods that allow remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9795
- https://issues.apache.org/jira/browse/GEODE-3247
- https://lists.apache.org/thread.html/0fc5ea3c1ea06fe7058a0ab56d593914b05f728a6c93c5a6755956c7@%3Cuser.geode.apache.org%3E
- https://lists.apache.org/thread.html/232d75150991820d2fe6ba6bd4265fb58b4fe4d9d8d62eb2fd97256c@%3Cdev.geode.apache.org%3E
- https://lists.apache.org/thread.html/3a48163ca1fff757aefa4d9df24a251bb11ddd599a78cd85585abd00@%3Cdev.geode.apache.org%3E
