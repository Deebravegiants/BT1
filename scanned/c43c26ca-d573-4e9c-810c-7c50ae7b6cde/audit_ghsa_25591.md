# [H] Prototype Pollution in nconf

## Summary
Severity: High
Advisory: GHSA-6xwr-q98w-rvg7
CVE: CVE-2022-21803
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-04-13
Source: https://github.com/advisories/GHSA-6xwr-q98w-rvg7
Type: github-advisory

## Affected
- npm: `nconf` — affected >=0 <0.11.4

## Details
nconf before 0.11.4. When using the memory engine, it is possible to store a nested JSON representation of the configuration. The .set() function, that is responsible for setting the configuration properties, is vulnerable to Prototype Pollution. By providing a crafted property, it is possible to modify the properties on the Object.prototype.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21803
- https://github.com/indexzero/nconf/pull/397
- https://github.com/indexzero/nconf
- https://github.com/indexzero/nconf/releases/tag/v0.11.4
- https://snyk.io/vuln/SNYK-JS-NCONF-2395478
