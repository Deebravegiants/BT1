# [M] Arbitrary javascript injection in Apache Jena

## Summary
Severity: Medium
Advisory: GHSA-xgh5-gwq5-rpx8
CVE: CVE-2023-22665
CWE: CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-25
Source: https://github.com/advisories/GHSA-xgh5-gwq5-rpx8
Type: github-advisory

## Affected
- Maven: `org.apache.jena:jena` — affected >=0 <4.8.0

## Details
There is insufficient checking of user queries in Apache Jena versions 4.7.0 and earlier, when invoking custom scripts. It allows a remote user to execute arbitrary javascript via a SPARQL query.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-22665
- https://github.com/apache/jena
- https://lists.apache.org/thread/s0dmpsxcwqs57l4qfs415klkgmhdxq7s
- http://www.openwall.com/lists/oss-security/2023/07/11/11
