# [H] Apache Geode configuration request authorization vulnerability

## Summary
Severity: High
Advisory: GHSA-g569-49wg-jx5f
CVE: CVE-2017-15696
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-g569-49wg-jx5f
Type: github-advisory

## Affected
- Maven: `org.apache.geode:geode-core` — affected >=1.0.0 <1.4.0

## Details
When an Apache Geode cluster before v1.4.0 is operating in secure mode, the Geode configuration service does not properly authorize configuration requests. This allows an unprivileged user who gains access to the Geode locator to extract configuration data and previously deployed application code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15696
- https://github.com/apache/geode/pull/1059
- https://github.com/apache/geode
- https://issues.apache.org/jira/browse/GEODE-3962
- https://lists.apache.org/thread.html/28989e6ed0d3c29e46a489ae508302a50407a40691d5dc968f78cd3f@%3Cdev.geode.apache.org%3E
