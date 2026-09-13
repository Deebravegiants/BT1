# [M] Prototype pollution in @tsed/core

## Summary
Severity: Medium
Advisory: GHSA-77xq-cpvg-7xm2
CVE: CVE-2020-7748
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-77xq-cpvg-7xm2
Type: github-advisory

## Affected
- npm: `@tsed/core` — affected >=0 <5.65.7

## Details
This affects the package @tsed/core before 5.65.7. This vulnerability relates to the `deepExtend` function which is used as part of the utils directory. Depending on if user input is provided, an attacker can overwrite and pollute the object prototype of a program.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7748
- https://github.com/TypedProject/tsed/commit/1395773ddac35926cf058fc6da9fb8e82266761b
- https://github.com/TypedProject/tsed/blob/production/packages/core/src/utils/deepExtends.ts%23L36
- https://github.com/tsedio/tsed
- https://snyk.io/vuln/SNYK-JS-TSEDCORE-1019382
