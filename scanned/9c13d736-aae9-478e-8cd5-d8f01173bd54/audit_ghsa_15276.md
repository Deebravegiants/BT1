# [C] Prototype pollution in izatop bunt

## Summary
Severity: Critical
Advisory: GHSA-p734-xg27-8cfq
CVE: CVE-2024-38989
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-12
Source: https://github.com/advisories/GHSA-p734-xg27-8cfq
Type: github-advisory

## Affected
- npm: `@bunt/app` — affected >=0 <0.29.26

## Details
izatop bunt v0.29.19 was discovered to contain a prototype pollution via the component /esm/qs.js. This vulnerability allows attackers to execute arbitrary code via injecting arbitrary properties.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38989
- https://github.com/izatop/bunt/issues/27
- https://github.com/izatop/bunt/commit/c55201a8cee03e5282f99874dead988c80d31db7
- https://gist.github.com/mestrtee/5e9830fb180a34d65f04fafb52d2b94b
- https://github.com/izatop/bunt
