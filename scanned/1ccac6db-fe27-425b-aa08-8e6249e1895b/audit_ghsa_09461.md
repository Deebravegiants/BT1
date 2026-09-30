# [H] Summarize contains a path traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-8jr4-6r33-phwm
CVE: CVE-2026-45242
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-8jr4-6r33-phwm
Type: github-advisory

## Affected
- npm: `@steipete/summarize` — affected >=0 <0.15.0

## Details
Summarize prior to 0.15.0 contains a path traversal vulnerability in the /v1/summarize daemon endpoint that allows authenticated callers to write files to arbitrary directories by supplying an absolute path or directory traversal sequence in the slidesDir request parameter. Attackers can exploit this to write slide_*.png and slides.json files to any writable directory and subsequently delete matching files at the specified location through repeat extraction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-45242
- https://github.com/steipete/summarize/pull/220
- https://github.com/steipete/summarize/commit/ec8efd63295656fbfe8743620179c489bc5a242f
- https://github.com/steipete/summarize
- https://github.com/steipete/summarize/releases/tag/v0.15.1
- https://github.com/steipete/summarize/releases/tag/v0.15.2
- https://www.vulncheck.com/advisories/summarize-path-traversal-via-slidesdir-parameter
