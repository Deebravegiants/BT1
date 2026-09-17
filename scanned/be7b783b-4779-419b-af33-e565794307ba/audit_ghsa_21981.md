# [H] Prototype Pollution in mout

## Summary
Severity: High
Advisory: GHSA-pc58-wgmc-hfjr
CVE: CVE-2020-7792
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-pc58-wgmc-hfjr
Type: github-advisory

## Affected
- npm: `mout` — affected >=0 <1.2.3

## Details
This affects all versions of package mout. The deepFillIn function can be used to 'fill missing properties recursively', while the deepMixIn 'mixes objects into the target object, recursively mixing existing child objects as well'. In both cases, the key used to access the target object recursively is not checked, leading to a Prototype Pollution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7792
- https://github.com/mout/mout/commit/3fecf1333e6d71ae72edf48c71dc665e40df7605
- https://github.com/mout/mout/blob/master/src/object/deepFillIn.js
- https://github.com/mout/mout/blob/master/src/object/deepMixIn.js
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARS-1050374
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1050373
- https://snyk.io/vuln/SNYK-JS-MOUT-1014544
