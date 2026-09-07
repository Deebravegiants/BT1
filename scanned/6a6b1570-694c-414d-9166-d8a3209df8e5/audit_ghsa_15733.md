# [M] Calibre-Web Cross Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-j22r-3rf3-cv25
CVE: CVE-2024-39123
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-07-19
Source: https://github.com/advisories/GHSA-j22r-3rf3-cv25
Type: github-advisory

## Affected
- PyPI: `calibreweb` — affected >=0.6.0

## Details
In janeczku Calibre-Web 0.6.0 to 0.6.21, the edit_book_comments function is vulnerable to Cross Site Scripting (XSS) due to improper sanitization performed by the clean_string function. The vulnerability arises from the way the clean_string function handles HTML sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39123
- https://github.com/janeczku/calibre-web
- https://github.com/pentesttoolscom/vulnerability-research/tree/master/CVE-2024-39123
