# [H] uPlot Prototype Pollution vulnerability

## Summary
Severity: High
Advisory: GHSA-34q8-jcq6-mc37
CVE: CVE-2024-21489
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2024-10-01
Source: https://github.com/advisories/GHSA-34q8-jcq6-mc37
Type: github-advisory

## Affected
- npm: `uplot` — affected >=0 <1.6.31

## Details
Versions of the package uplot before 1.6.31 are vulnerable to Prototype Pollution via the uplot.assign function due to missing check if the attribute resolves to the object prototype.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21489
- https://github.com/leeoniya/uPlot/commit/5756e3e9b91270b303157e14bd0174311047d983
- https://github.com/leeoniya/uPlot
- https://github.com/leeoniya/uPlot/blob/c52e5001c1d959a99ac495a53e4deca5c44464d2/src/utils.js#L437-L452
- https://security.snyk.io/vuln/SNYK-JS-UPLOT-6209224
