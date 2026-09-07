# [M] csaf-poc/csaf_distribution Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xxfx-w2rw-gh63
CVE: CVE-2022-43996
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-14
Source: https://github.com/advisories/GHSA-xxfx-w2rw-gh63
Type: github-advisory

## Affected
- Go: `github.com/csaf-poc/csaf_distribution` — affected >=0 <0.8.2

## Details
The csaf_provider package before 0.8.2 allows XSS via a crafted CSAF document uploaded as text/html. The endpoint upload allows valid CSAF advisories (JSON format) to be uploaded with Content-Type text/html and filenames ending in .html. When subsequently accessed via web browser, these advisories are served and interpreted as HTML pages. Such uploaded advisories can contain JavaScript code that will execute within the browser context of users inspecting the advisory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43996
- https://github.com/csaf-poc/csaf_distribution/commit/17f22855ee8d4270dd17ff748c30ed7304846fdc
- https://github.com/csaf-poc/csaf_distribution
- https://github.com/csaf-poc/csaf_distribution/releases/tag/v0.8.2
- https://wid.cert-bund.de/.well-known/csaf/white/2022/bsi-2022-0003.json
