# [H] Apache Ambari Expression Language Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-p7w2-784m-qpq9
CVE: CVE-2022-45855
CWE: CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-p7w2-784m-qpq9
Type: github-advisory

## Affected
- Maven: `org.apache.ambari:ambari` — affected >=2.7.0 <2.7.7

## Details
SpringEL injection in the metrics source in Apache Ambari version 2.7.0 to 2.7.6 allows a malicious authenticated user to execute arbitrary code remotely. Users are recommended to upgrade to 2.7.7.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45855
- https://github.com/apache/ambari
- https://lists.apache.org/thread/302c4hwfjy9lx63jrbhcdx948pxc54l1
