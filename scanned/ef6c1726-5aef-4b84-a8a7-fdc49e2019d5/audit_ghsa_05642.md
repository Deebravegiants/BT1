# [H] billboard.js is vulnerable to XSS during chart option binding

## Summary
Severity: High
Advisory: GHSA-rpc5-pm7q-hjmp
CVE: CVE-2026-1513
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-01-28
Source: https://github.com/advisories/GHSA-rpc5-pm7q-hjmp
Type: github-advisory

## Affected
- npm: `billboard.js` — affected >=0 <3.18.0

## Details
billboard.js before 3.18.0 allows an attacker to execute malicious JavaScript due to improper sanitization during chart option binding.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1513
- https://github.com/naver/billboard.js/issues/4078
- https://github.com/naver/billboard.js/commit/49e079cdd466fc8ba7ab208988181e5b7a5f336b
- https://cve.naver.com/detail/cve-2026-1513.html
- https://github.com/naver/billboard.js
