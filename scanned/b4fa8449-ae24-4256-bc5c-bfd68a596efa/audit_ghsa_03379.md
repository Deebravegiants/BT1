# [H] Cross-site Scripting (XSS) in @scullyio/scully

## Summary
Severity: High
Advisory: GHSA-r96p-v3cr-gfv8
CVE: CVE-2020-28470
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-r96p-v3cr-gfv8
Type: github-advisory

## Affected
- npm: `@scullyio/scully` — affected >=0 <1.0.9
- npm: `@scullyio/ng-lib` — affected >=0 <1.0.1

## Details
This affects the package @scullyio/scully before 1.0.9. The transfer state is serialised with the JSON.stringify() function and then written into the HTML page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28470
- https://github.com/scullyio/scully/pull/1182
- https://github.com/scullyio/scully
- https://snyk.io/vuln/SNYK-JS-SCULLYIOSCULLY-1055829
