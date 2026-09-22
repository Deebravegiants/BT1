# [H] Prototype Pollution in mout

## Summary
Severity: High
Advisory: GHSA-vvv8-xw5f-3f88
CVE: CVE-2022-21213
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-18
Source: https://github.com/advisories/GHSA-vvv8-xw5f-3f88
Type: github-advisory

## Affected
- npm: `mout` — affected >=0 <1.2.4

## Details
This affects all versions of package mout. The deepFillIn function can be used to 'fill missing properties recursively', while the deepMixIn mixes objects into the target object, recursively mixing existing child objects as well. In both cases, the key used to access the target object recursively is not checked, leading to exploiting this vulnerability. **Note:** This vulnerability derives from an incomplete fix of [CVE-2020-7792](https://security.snyk.io/vuln/SNYK-JS-MOUT-1014544).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21213
- https://github.com/mout/mout/pull/279
- https://github.com/mout/mout/commit/17ffdc2a96417a63a0147156dc045e90d0d14c64
- https://github.com/mout/mout
- https://github.com/mout/mout/blob/master/src/object/deepFillIn.js
- https://github.com/mout/mout/blob/master/src/object/deepMixIn.js
- https://snyk.io/vuln/SNYK-JS-MOUT-2342654
