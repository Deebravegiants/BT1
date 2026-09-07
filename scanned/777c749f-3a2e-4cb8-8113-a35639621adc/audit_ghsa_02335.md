# [M] Cross-site scripting in Apache Jena Fuseki

## Summary
Severity: Medium
Advisory: GHSA-phwj-86vx-cfjc
CVE: CVE-2021-33192
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-08-13
Source: https://github.com/advisories/GHSA-phwj-86vx-cfjc
Type: github-advisory

## Affected
- Maven: `org.apache.jena:jena-fuseki` — affected >=2.0.0 <4.1.0

## Details
A vulnerability in the HTML pages of Apache Jena Fuseki allows an attacker to execute arbitrary javascript on certain page views. This issue affects Apache Jena Fuseki from version 2.0.0 to version 4.0.0 (inclusive).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33192
- https://lists.apache.org/thread.html/r684d8943d755a96fe90f8cd8df196737b6bde3f2b74e15a9bd479975%40%3Cusers.jena.apache.org%3E
