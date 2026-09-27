# [C] obx Prototype Pollution

## Summary
Severity: Critical
Advisory: GHSA-jj58-488v-4rgf
CVE: CVE-2024-36573
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-17
Source: https://github.com/advisories/GHSA-jj58-488v-4rgf
Type: github-advisory

## Affected
- npm: `@almela/obx` — affected >=0 <0.0.4

## Details
almela obx before v.0.0.4 has a Prototype Pollution issue which allows arbitrary code execution via the obx/build/index.js:656), reduce (@almela/obx/build/index.js:470), Object.set (obx/build/index.js:269) component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36573
- https://github.com/llGaetanll/obx/commit/984ad92dc06774da4e6bdae0f5f5e59ae80ece8f
- https://gist.github.com/mestrtee/fd8181bbc180d775f8367a2b9e0ffcd1
- https://github.com/llGaetanll/obx
