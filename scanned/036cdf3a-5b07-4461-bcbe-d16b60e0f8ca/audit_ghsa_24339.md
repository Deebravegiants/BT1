# [M] Apache Geode OQL bind parameter vulnerability

## Summary
Severity: Medium
Advisory: GHSA-q7cp-r6cj-hpf5
CVE: CVE-2017-9796
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-q7cp-r6cj-hpf5
Type: github-advisory

## Affected
- Maven: `org.apache.geode:geode-core` — affected >=1.0.0 <1.3.0

## Details
When an Apache Geode cluster before v1.3.0 is operating in secure mode, a user with read access to specific regions within a Geode cluster may execute OQL queries containing a region name as a bind parameter that allow read access to objects within unauthorized regions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9796
- https://issues.apache.org/jira/browse/GEODE-3248
- https://lists.apache.org/thread.html/e580d22195b6b61ff9cf866ac6dd6fe16e790ff0e14a3b1a22cd20b1@%3Cuser.geode.apache.org%3E
