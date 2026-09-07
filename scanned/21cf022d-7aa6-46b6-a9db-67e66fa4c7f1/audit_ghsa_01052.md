# [H] Denial of Service in markdown-it-toc-and-anchor

## Summary
Severity: High
Advisory: GHSA-x6m6-5hrf-fh6r
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-x6m6-5hrf-fh6r
Type: github-advisory

## Affected
- npm: `markdown-it-toc-and-anchor` — affected >=0 <4.2.0

## Details
All versions of `markdown-it-toc-and-anchor` are vulnerable to Denial of Service. Parsing markdown containing `**text**+\n@[toc]` causes the application to enter and infinite loop.


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://github.com/medfreeman/markdown-it-toc-and-anchor
- https://snyk.io/vuln/SNYK-JS-MARKDOWNITTOCANDANCHOR-73500
- https://www.npmjs.com/advisories/749
