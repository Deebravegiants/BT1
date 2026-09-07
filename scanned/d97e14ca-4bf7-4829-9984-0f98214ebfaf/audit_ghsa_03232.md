# [H] Prototype Pollution in simpl-schema

## Summary
Severity: High
Advisory: GHSA-9mx2-prfp-8hqp
CVE: CVE-2020-7742
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-9mx2-prfp-8hqp
Type: github-advisory

## Affected
- npm: `simpl-schema` — affected >=0 <1.10.2

## Details
This affects the package simpl-schema before 1.10.2. Attacker controlled input into a schema could result in remote code execution within the scope of the surrounding application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7742
- https://github.com/longshotlabs/simpl-schema/commit/50128841fa7fc2d137c36a397054279144caea3d
- https://github.com/longshotlabs/simpl-schema/releases/tag/1.10.2
- https://snyk.io/vuln/SNYK-JS-SIMPLSCHEMA-1016157
