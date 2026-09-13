# [C] Prototype Pollution in set-in

## Summary
Severity: Critical
Advisory: GHSA-6956-83fg-5wc5
CVE: CVE-2022-25354
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-6956-83fg-5wc5
Type: github-advisory

## Affected
- npm: `set-in` — affected >=0 <2.0.3

## Details
The package set-in before 2.0.3 is vulnerable to Prototype Pollution via the `setIn` method, as it allows an attacker to merge object prototypes into it. **Note:** This vulnerability derives from an incomplete fix of [CVE-2020-28273](https://security.snyk.io/vuln/SNYK-JS-SETIN-1048049)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25354
- https://github.com/ahdinosaur/set-in/commit/6bad255961d379e4b1f5fbc52ef9dc8420816f24
- https://github.com/ahdinosaur/set-in
- https://github.com/ahdinosaur/set-in/blob/dfc226d95cce8129de6708661e06e0c2c06f3490/index.js%23L5
- https://snyk.io/vuln/SNYK-JS-SETIN-2388571
