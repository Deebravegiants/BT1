# [H] @stryker-mutator/util vulnerable to Prototype Pollution

## Summary
Severity: High
Advisory: GHSA-9j5q-479x-43g2
CVE: CVE-2024-57085
CWE: CWE-1321, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-02-06
Source: https://github.com/advisories/GHSA-9j5q-479x-43g2
Type: github-advisory

## Affected
- npm: `@stryker-mutator/util` — affected >=0 <8.7.1

## Details
A prototype pollution in the function deepMerge of @stryker-mutator/util v8.6.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57085
- https://github.com/stryker-mutator/stryker-js/issues/5144
- https://github.com/stryker-mutator/stryker-js/commit/f7b34bfbbde33e45bc213a2f6058bf0c5bf6bce7
- https://gist.github.com/tariqhawis/f59355f62dad6f8b53b42317f143ba0c
- https://github.com/stryker-mutator/stryker-js
- https://github.com/stryker-mutator/stryker-js/blob/7270f111ff36d6b18669302f5702fd42f664d53e/CHANGELOG.md#871-2024-12-11
