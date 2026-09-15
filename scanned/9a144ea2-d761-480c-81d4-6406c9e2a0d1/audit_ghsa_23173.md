# [H] Apache Geode gfsh authorization vulnerability

## Summary
Severity: High
Advisory: GHSA-h22r-h77w-2g5f
CVE: CVE-2017-12622
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-h22r-h77w-2g5f
Type: github-advisory

## Affected
- Maven: `org.apache.geode:geode-core` — affected >=1.0.0 <1.3.0

## Details
When an Apache Geode cluster before v1.3.0 is operating in secure mode and an authenticated user connects to a Geode cluster using the gfsh tool with HTTP, the user is able to obtain status information and control cluster members even without CLUSTER:MANAGE privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12622
- https://issues.apache.org/jira/browse/GEODE-3685
- https://lists.apache.org/thread.html/560578479dabbdc93d0ee8746b7c857549202ef82f43aa22496aa589@%3Cuser.geode.apache.org%3E
