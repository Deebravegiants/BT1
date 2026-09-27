# [H] lilconfig Code Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-fq9m-v26v-2m4f
CVE: CVE-2024-21537
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-31
Source: https://github.com/advisories/GHSA-fq9m-v26v-2m4f
Type: github-advisory

## Affected
- npm: `lilconfig` — affected >=3.1.0 <3.1.1

## Details
Versions of the package lilconfig from 3.1.0 and before 3.1.1 are vulnerable to Arbitrary Code Execution due to the insecure usage of eval in the dynamicImport function. An attacker can exploit this vulnerability by passing a malicious input through the defaultLoaders function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21537
- https://github.com/antonk52/lilconfig/pull/48
- https://github.com/antonk52/lilconfig/commit/2c68a1ab8764fc74acc46771e1ad39ab07a9b0a7
- https://github.com/antonk52/lilconfig
- https://github.com/antonk52/lilconfig/releases/tag/v3.1.1
- https://security.snyk.io/vuln/SNYK-JS-LILCONFIG-6263789
