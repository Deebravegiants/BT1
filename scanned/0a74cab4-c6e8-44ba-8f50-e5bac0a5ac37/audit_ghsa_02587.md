# [M] Type confusion in mpath

## Summary
Severity: Medium
Advisory: GHSA-p92x-r36w-9395
CVE: CVE-2021-23438
CWE: CWE-843
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-p92x-r36w-9395
Type: github-advisory

## Affected
- npm: `mpath` — affected >=0 <0.8.4

## Details
This affects the package mpath before 0.8.4. A type confusion vulnerability can lead to a bypass of CVE-2018-16490. In particular, the condition `ignoreProperties.indexOf(parts[i]) !== -1` returns `-1` if `parts[i]` is `['__proto__']`. This is because the method that has been called if the input is an array is `Array.prototype.indexOf()` and not `String.prototype.indexOf()`. They behave differently depending on the type of the input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23438
- https://github.com/aheckmann/mpath/commit/89402d2880d4ea3518480a8c9847c541f2d824fc
- https://github.com/mongoosejs/mpath/commit/89402d2880d4ea3518480a8c9847c541f2d824fc
- https://github.com/aheckmann/mpath
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1579548
- https://snyk.io/vuln/SNYK-JS-MPATH-1577289
