# [M] Browsershot vulnerable to Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-82h9-v8vh-mfpq
CVE: CVE-2022-43983
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-25
Source: https://github.com/advisories/GHSA-82h9-v8vh-mfpq
Type: github-advisory

## Affected
- Packagist: `spatie/browsershot` — affected >=0 <3.57.3

## Details
Browsershot version 3.57.2 allows an external attacker to remotely obtain arbitrary local files. This is possible because the application does not validate that the HTML content passed to the Browsershot::html method does not contain URL's that use the file:// protocol.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43983
- https://github.com/spatie/browsershot/commit/92cf16fc098211731f80d21687abeafbe2c457ad
- https://fluidattacks.com/advisories/khalid
- https://github.com/spatie/browsershot
