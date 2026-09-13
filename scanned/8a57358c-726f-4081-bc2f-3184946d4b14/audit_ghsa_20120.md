# [C] vm2 vulnerable to Arbitrary Code Execution

## Summary
Severity: Critical
Advisory: GHSA-4w2j-2rg4-5mjw
CVE: CVE-2022-25893
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-21
Source: https://github.com/advisories/GHSA-4w2j-2rg4-5mjw
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.9.10

## Details
The package vm2 before 3.9.10 is vulnerable to Arbitrary Code Execution due to the usage of prototype lookup for the WeakMap.prototype.set method. Exploiting this vulnerability leads to access to a host object and a sandbox compromise.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25893
- https://github.com/patriksimek/vm2/issues/444
- https://github.com/patriksimek/vm2/pull/445
- https://github.com/patriksimek/vm2/pull/445/commits/3a9876482be487b78a90ac459675da7f83f46d69
- https://github.com/patriksimek/vm2
- https://security.snyk.io/vuln/SNYK-JS-VM2-2990237
