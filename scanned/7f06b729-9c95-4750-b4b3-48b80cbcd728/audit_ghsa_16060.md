# [M] FitNesse Cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-pg82-9w35-3w3r
CVE: CVE-2024-39610
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-11-15
Source: https://github.com/advisories/GHSA-pg82-9w35-3w3r
Type: github-advisory

## Affected
- Maven: `org.fitnesse:fitnesse` — affected >=0 <20241026

## Details
Cross-site scripting vulnerability exists in FitNesse releases prior to 20241026. If this vulnerability is exploited, an arbitrary script may be executed on the web browser of the user who is using the product.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39610
- https://fitnesse.org/FitNesseDownload
- https://github.com/unclebob/fitnesse
- https://github.com/unclebob/fitnesse/releases/tag/20241026
- https://jvn.jp/en/jp/JVN36791327
