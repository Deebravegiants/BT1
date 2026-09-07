# [M] Uncontrolled Resource Consumption in firebase

## Summary
Severity: Medium
Advisory: GHSA-fpm5-vv97-jfwg
CVE: CVE-2020-7765
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-fpm5-vv97-jfwg
Type: github-advisory

## Affected
- npm: `@firebase/util` — affected >=0 <0.3.4

## Details
This affects the package @firebase/util before 0.3.4. This vulnerability relates to the deepExtend function within the DeepCopy.ts file. Depending on if user input is provided, an attacker can overwrite and pollute the object prototype of a program.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7765
- https://github.com/firebase/firebase-js-sdk/pull/4001
- https://github.com/firebase/firebase-js-sdk/commit/9cf727fcc3d049551b16ae0698ac33dc2fe45ada
- https://snyk.io/vuln/SNYK-JS-FIREBASEUTIL-1038324
