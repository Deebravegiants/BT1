# [M] Prototype Pollution in undefsafe

## Summary
Severity: Medium
Advisory: GHSA-332q-7ff2-57h2
CVE: CVE-2019-10795
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-332q-7ff2-57h2
Type: github-advisory

## Affected
- npm: `undefsafe` — affected >=0 <2.0.3

## Details
undefsafe before 2.0.3 is vulnerable to Prototype Pollution. The 'a' function could be tricked into adding or modifying properties of Object.prototype using a `__proto__` payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10795
- https://github.com/remy/undefsafe/commit/f272681b3a50e2c4cbb6a8533795e1453382c822
- https://github.com/remy/undefsafe
- https://snyk.io/vuln/SNYK-JS-UNDEFSAFE-548940
