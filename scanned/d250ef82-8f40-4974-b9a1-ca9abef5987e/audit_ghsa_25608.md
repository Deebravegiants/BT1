# [H] Prototype Pollution in deepmerge-ts

## Summary
Severity: High
Advisory: GHSA-r9w3-g83q-m6hq
CVE: CVE-2022-24802
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-01
Source: https://github.com/advisories/GHSA-r9w3-g83q-m6hq
Type: github-advisory

## Affected
- npm: `deepmerge-ts` — affected >=0 <4.0.2

## Details
deepmerge-ts is used to merge 2 or more objects respecting type information. deepmerge-ts is vulnerable to Prototype Pollution via file deepmerge.ts, function defaultMergeRecords(). A fix was released in version 4.0.2. Currently, there is no known workaround.

## References
- https://github.com/RebeccaStevens/deepmerge-ts/security/advisories/GHSA-r9w3-g83q-m6hq
- https://nvd.nist.gov/vuln/detail/CVE-2022-24802
- https://github.com/RebeccaStevens/deepmerge-ts/commit/b39f1a93d9e1c3541bd2fe159fd696a16dbe1c72
- https://github.com/RebeccaStevens/deepmerge-ts/commit/d637db7e4fb2bfb113cb4bc1c85a125936d7081b
- https://github.com/RebeccaStevens/deepmerge-ts
