# [M] Outdated Static Dependency in vue-moment

## Summary
Severity: Medium
Advisory: GHSA-hrpp-f84w-xhfg
CWE: CWE-1104
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-hrpp-f84w-xhfg
Type: github-advisory

## Affected
- npm: `vue-moment` — affected >=0 <4.1.0

## Details
Versions of `vue-moment` prior to 4.1.0 contain an Outdated Static Dependency. The package depends on `moment` and has it loaded statically instead of as a dependency that can be updated. It has `moment@2.19.1` that contains a Regular Expression Denial of Service vulnerability.


## Recommendation

Upgrade to version 4.1.0 or later.

## References
- https://github.com/brockpetrie/vue-moment/commit/a265e54660a7181a6795a12a97cebac5b305746e
- https://github.com/brockpetrie/vue-moment
- https://snyk.io/vuln/SNYK-JS-VUEMOMENT-538934
- https://www.npmjs.com/advisories/1425
- https://www.npmjs.com/advisories/532
