# [C] Apache Geode unsafe deserialization in TcpServer

## Summary
Severity: Critical
Advisory: GHSA-w395-hpq9-7xwr
CVE: CVE-2017-15692
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-w395-hpq9-7xwr
Type: github-advisory

## Affected
- Maven: `org.apache.geode:geode-core` — affected >=1.0.0 <1.4.0

## Details
In Apache Geode before v1.4.0, the TcpServer within the Geode locator opens a network port that deserializes data. If an unprivileged user gains access to the Geode locator, they may be able to cause remote code execution if certain classes are present on the classpath.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15692
- https://github.com/apache/geode/pull/1166
- https://issues.apache.org/jira/browse/GEODE-3923
- https://lists.apache.org/thread/dctjhhjtomnsk625dj90dg4sgm438k0k
