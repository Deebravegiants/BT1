# [M] Improper Input Validation vulnerability in Apache Hop Engine

## Summary
Severity: Medium
Advisory: GHSA-f6g6-pjgc-5cj5
CVE: CVE-2024-24683
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-03-19
Source: https://github.com/advisories/GHSA-f6g6-pjgc-5cj5
Type: github-advisory

## Affected
- Maven: `org.apache.hop:hop` — affected >=0 <2.8.0

## Details
Improper Input Validation vulnerability in Apache Hop Engine. This issue affects Apache Hop Engine: before 2.8.0.

Users are recommended to upgrade to version 2.8.0, which fixes the issue.

When Hop Server writes links to the PrepareExecutionPipelineServlet page one of the parameters provided to the user was not properly escaped.
The variable not properly escaped is the "id", which is not directly accessible by users creating pipelines making the risk of exploiting this low.

This issue only affects users using the Hop Server component and does not directly affect the client.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-24683
- https://github.com/apache/hop
- https://lists.apache.org/thread/ts203zssv1n9qth1wdlhk2bhos3vcq6t
- http://www.openwall.com/lists/oss-security/2024/03/18/1
