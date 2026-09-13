# [M] Improper Certificate Validation in node-sass

## Summary
Severity: Medium
Advisory: GHSA-r8f7-9pfq-mjmv
CVE: CVE-2020-24025
CWE: CWE-295
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-r8f7-9pfq-mjmv
Type: github-advisory

## Affected
- npm: `node-sass` — affected >=2.0.0 <7.0.0

## Details
Certificate validation in node-sass 2.0.0 to 6.0.1 is disabled when requesting binaries even if the user is not specifying an alternative download path.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24025
- https://github.com/sass/node-sass/issues/3067
- https://github.com/sass/node-sass/pull/3149
- https://github.com/sass/node-sass/pull/567#issuecomment-656609236
- https://github.com/sass/node-sass/commit/0a21792803639851b480fbd8cbcb5540ef974387
- https://github.com/sass/node-sass
- https://github.com/sass/node-sass/releases/tag/v7.0.0
