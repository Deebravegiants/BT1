# [M] Complianz WordPress plugin vulnerable to cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-7j4m-f87g-5r9r
CVE: CVE-2023-1069
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-27
Source: https://github.com/advisories/GHSA-7j4m-f87g-5r9r
Type: github-advisory

## Affected
- Packagist: `really-simple-plugins/complianz-gdpr` — affected >=0 <6.4.2

## Details
The Complianz Premium WordPress plugin before 6.4.2 did not validate and escape some of its shortcode attributes before outputting them back in a page/post where the shortcode is embed, which could allow users with the contributor role and above to perform Stored Cross-Site Scripting attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1069
- https://github.com/Really-Simple-Plugins/complianz-gdpr/commit/e6c2c386cadb78f8cdcded1b000cbd38bd9ff043
- https://wpscan.com/vulnerability/caacc50c-822e-46e9-bc0b-681349fd0dda
- www.github.com/Really-Simple-Plugins/complianz-gdpr
