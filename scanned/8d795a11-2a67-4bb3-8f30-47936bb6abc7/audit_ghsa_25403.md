# [H] Apache Atlas produces Stack trace in error response

## Summary
Severity: High
Advisory: GHSA-fx92-wh72-8g9q
CVE: CVE-2017-3154
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-fx92-wh72-8g9q
Type: github-advisory

## Affected
- Maven: `org.apache.atlas:atlas-common` — affected >=0.6.0-incubating <0.7.1-incubating

## Details
Error responses from Apache Atlas versions 0.6.0-incubating and 0.7.0-incubating included stack trace, exposing excessive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-3154
- https://github.com/apache/atlas
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-atlas/PYSEC-2017-110.yaml
- https://lists.apache.org/thread.html/4a4fef91e067fd0d9da569e30867c1fa65e2a0520acde71ddefee0ea%40%3Cdev.atlas.apache.org%3E
- https://lists.apache.org/thread.html/4a4fef91e067fd0d9da569e30867c1fa65e2a0520acde71ddefee0ea@%3Cdev.atlas.apache.org%3E
- http://www.securityfocus.com/bid/100581
