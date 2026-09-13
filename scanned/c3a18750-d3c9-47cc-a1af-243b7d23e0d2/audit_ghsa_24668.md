# [H] Apache Geode vulnerable to Incorrect Authorization

## Summary
Severity: High
Advisory: GHSA-jmg4-x4vp-6c6x
CVE: CVE-2017-15695
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-jmg4-x4vp-6c6x
Type: github-advisory

## Affected
- Maven: `org.apache.geode:geode-core` — affected >=1.0.0 <1.5.0

## Details
When an Apache Geode server versions 1.0.0 to 1.4.0 is configured with a security manager, a user with DATA:WRITE privileges is allowed to deploy code by invoking an internal Geode function. This allows remote code execution. Code deployment should be restricted to users with DATA:MANAGE privilege.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15695
- https://github.com/apache/geode/pull/1258
- https://github.com/apache/geode/commit/00be4f9774e1adf8e7ccc2664da8005fc30bb11d
- https://github.com/apache/geode/commit/49d28f93fd2ef069693ce15d124ef3a29f22fb7d
- https://github.com/apache/geode/commit/6df14c8b1e3c644f9f810149e80bba0c2f073dab
- https://github.com/apache/geode/commit/740289c61d60256c6270756bc84b9e24b76e4913
- https://github.com/apache/geode/commit/90f8f6242927c5e16da64f38bba9abf3d450a305
- https://github.com/apache/geode/commit/954ccb545d24a9c9a35cbd84023a4d7e07032de0
- https://github.com/apache/geode/commit/aa469239860778eb46e09dd7b390aee08f152480
- https://cwiki.apache.org/confluence/display/GEODE/Release+Notes#ReleaseNotes-SecurityVulnerabilities
- https://github.com/apache/geode
- https://issues.apache.org/jira/browse/GEODE-3974
- https://lists.apache.org/thread.html/dc8875c0b924885a884eba6d5bd7dc3f123411b2d33cffd00e351c99@%3Cuser.geode.apache.org%3E
