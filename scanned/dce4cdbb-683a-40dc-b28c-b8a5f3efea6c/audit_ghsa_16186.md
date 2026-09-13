# [M] FitNesse Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-q297-5ff8-hc92
CVE: CVE-2024-42499
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-11-15
Source: https://github.com/advisories/GHSA-q297-5ff8-hc92
Type: github-advisory

## Affected
- Maven: `org.fitnesse:fitnesse` — affected >=0 <20241026

## Details
Improper limitation of a pathname to a restricted directory ('Path Traversal') issue exists in FitNesse releases prior to 20241026. If this vulnerability is exploited, an attacker may be able to know whether a file exists at a specific path, and/or obtain some part of the file contents under specific conditions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-42499
- https://github.com/unclebob/fitnesse/commit/850c599e5177d6f877af063374086f3e36b4b956
- https://fitnesse.org/FitNesseDownload
- https://github.com/unclebob/fitnesse
- https://github.com/unclebob/fitnesse/releases/tag/20241026
- https://jvn.jp/en/jp/JVN36791327
