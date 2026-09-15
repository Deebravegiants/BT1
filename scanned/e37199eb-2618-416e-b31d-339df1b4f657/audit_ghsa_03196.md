# [H] Insecure template handling in Squirrelly

## Summary
Severity: High
Advisory: GHSA-q8j6-pwqx-pm96
CVE: CVE-2021-32819
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-05-17
Source: https://github.com/advisories/GHSA-q8j6-pwqx-pm96
Type: github-advisory

## Affected
- npm: `squirrelly` — affected >=0 <9.0.0

## Details
Squirrelly is a template engine implemented in JavaScript that works out of the box with ExpressJS. Squirrelly mixes pure template data with engine configuration options through the Express render API. By overwriting internal configuration options remote code execution may be triggered in downstream applications. Version 9.0.0 has a fix for this issue. For complete details refer to the referenced [GHSL-2021-023](https://securitylab.github.com/advisories/GHSL-2021-023-squirrelly/).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32819
- https://github.com/squirrellyjs/squirrelly/pull/254
- https://github.com/squirrellyjs/squirrelly/commit/c12418a026f73df645ba927fd29358efe02fed1e
- https://github.com/squirrellyjs/squirrelly/commit/dca7a1e7ee91d8a6ffffb655f3f15647486db9da
- https://github.com/squirrellyjs/squirrelly
- https://securitylab.github.com/advisories/GHSL-2021-023-squirrelly
