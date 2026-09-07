# [H] markdown-pdf vulnerable to local file read via server side cross-site scripting (XSS)

## Summary
Severity: High
Advisory: GHSA-qghr-877h-f9jh
CVE: CVE-2023-0835
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-04-05
Source: https://github.com/advisories/GHSA-qghr-877h-f9jh
Type: github-advisory

## Affected
- npm: `markdown-pdf` — affected >=0

## Details
markdown-pdf version 11.0.0 allows an external attacker to remotely obtain arbitrary local files. This is possible because the application does not validate the Markdown content entered by the user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0835
- https://fluidattacks.com/advisories/relsb
- https://github.com/alanshaw/markdown-pdf
- https://www.npmjs.com/package/markdown-pdf
