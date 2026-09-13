# [H] SketchSVG Arbitrary Code Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-6722-xvq8-3254
CVE: CVE-2023-26107
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-06
Source: https://github.com/advisories/GHSA-6722-xvq8-3254
Type: github-advisory

## Affected
- npm: `sketchsvg` — affected >=0

## Details
All versions of the package sketchsvg are vulnerable to Arbitrary Code Injection when invoking `shell.exec` without sanitization nor parametrization while concatenating the current directory as part of the command string.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26107
- https://github.com/eBay/SketchSVG
- https://github.com/eBay/SketchSVG/blob/dd1036648f0f320a3187ef79d506b676b9eb87a6/lib/index.js#23L115
- https://github.com/eBay/SketchSVG/blob/dd1036648f0f320a3187ef79d506b676b9eb87a6/lib/index.js#23L64
- https://security.snyk.io/vuln/SNYK-JS-SKETCHSVG-3167969
