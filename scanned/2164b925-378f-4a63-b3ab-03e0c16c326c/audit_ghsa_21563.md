# [H] Browsershot does not validate URL protocols passed to Browsershot URL method

## Summary
Severity: High
Advisory: GHSA-8c2c-jxwj-jqgf
CVE: CVE-2022-41706
CWE: CWE-20, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2022-11-25
Source: https://github.com/advisories/GHSA-8c2c-jxwj-jqgf
Type: github-advisory

## Affected
- Packagist: `spatie/browsershot` — affected >=0 <3.57.3

## Details
Browsershot version 3.57.2 allows an external attacker to remotely obtain arbitrary local files. This is possible because the application does not validate the URL protocol passed to the Browsershot::url method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41706
- https://github.com/spatie/browsershot/commit/92cf16fc098211731f80d21687abeafbe2c457ad
- https://fluidattacks.com/advisories/eminem
- https://github.com/spatie/browsershot
