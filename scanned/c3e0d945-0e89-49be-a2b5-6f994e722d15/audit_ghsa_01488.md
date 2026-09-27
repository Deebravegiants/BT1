# [M] Prototype Pollution in sds

## Summary
Severity: Medium
Advisory: GHSA-cxm3-284p-qc4v
CVE: CVE-2020-7618
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-cxm3-284p-qc4v
Type: github-advisory

## Affected
- npm: `sds` — affected >=0 <4.0.0

## Details
Affected versions of `sds` are vulnerable to prototype pollution. The `set` function does not restrict the modification of an Object's prototype, which may allow an attacker to add or modify an existing property that will exist on all objects.

## Recommendation

Upgrade to version 4.0.0 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7618
- https://github.com/monsterkodi/sds/blob/master/js/set.js#L31
- https://snyk.io/vuln/SNYK-JS-SDS-564123
- https://www.npmjs.com/advisories/1506
