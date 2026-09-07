# [M] Denial of Service in js-yaml

## Summary
Severity: Medium
Advisory: GHSA-2pr6-76vf-7546
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-06-05
Source: https://github.com/advisories/GHSA-2pr6-76vf-7546
Type: github-advisory

## Affected
- npm: `js-yaml` — affected >=0 <3.13.0

## Details
Versions of `js-yaml` prior to 3.13.0 are vulnerable to Denial of Service. By parsing a carefully-crafted YAML file, the node process stalls and may exhaust system resources leading to a Denial of Service.


## Recommendation

Upgrade to version 3.13.0.

## References
- https://github.com/nodeca/js-yaml/issues/475
- https://github.com/nodeca/js-yaml/commit/a567ef3c6e61eb319f0bfc2671d91061afb01235
- https://snyk.io/vuln/SNYK-JS-JSYAML-173999
- https://www.npmjs.com/advisories/788
- https://www.npmjs.com/advisories/788/versions
