# [H] Cross-Site Scripting in scratch-svg-renderer

## Summary
Severity: High
Advisory: GHSA-j977-g5vj-j27g
CVE: CVE-2020-7750
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2020-11-09
Source: https://github.com/advisories/GHSA-j977-g5vj-j27g
Type: github-advisory

## Affected
- npm: `scratch-svg-renderer` — affected >=0 <0.2.0-prerelease.20201019174008

## Details
This affects the package scratch-svg-renderer before 0.2.0-prerelease.20201019174008. The loadString function does not escape SVG properly, which can be used to inject arbitrary elements into the DOM via the _transformMeasurements function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7750
- https://github.com/LLK/scratch-svg-renderer/commit/9ebf57588aa596c4fa3bb64209e10ade395aee90
- https://snyk.io/vuln/SNYK-JS-SCRATCHSVGRENDERER-1020497
