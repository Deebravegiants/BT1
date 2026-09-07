# [H] Cross-site Scripting in electron-pdf

## Summary
Severity: High
Advisory: GHSA-3jcv-5f9p-2f2p
CVE: CVE-2024-1648
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-3jcv-5f9p-2f2p
Type: github-advisory

## Affected
- npm: `electron-pdf` — affected >=0

## Details
electron-pdf version 20.0.0 allows an external attacker to remotely obtain

arbitrary local files. This is possible because the application does not

validate the HTML content entered by the user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1648
- https://fluidattacks.com/advisories/drake
