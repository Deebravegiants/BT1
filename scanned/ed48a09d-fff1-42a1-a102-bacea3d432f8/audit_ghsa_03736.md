# [C] Arbitrary Code Execution in eslint-utils

## Summary
Severity: Critical
Advisory: GHSA-3gx7-xhv7-5mx3
CVE: CVE-2019-15657
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-08-26
Source: https://github.com/advisories/GHSA-3gx7-xhv7-5mx3
Type: github-advisory

## Affected
- npm: `eslint-utils` — affected >=1.2.0 <1.4.1

## Details
Versions of `eslint-utils` >=1.2.0 or <1.4.1 are vulnerable to Arbitrary Code Execution. The `getStaticValue` does not properly sanitize user input allowing attackers to supply malicious input that executes arbitrary code during the linting process. The `getStringIfConstant` and `getPropertyName` functions are not affected.


## Recommendation

Upgrade to version 1.4.1 or later.

## References
- https://github.com/mysticatea/eslint-utils/security/advisories/GHSA-3gx7-xhv7-5mx3
- https://nvd.nist.gov/vuln/detail/CVE-2019-15657
- https://github.com/mysticatea/eslint-utils/commit/08158db1c98fd71cf0f32ddefbc147e2620e724c
- https://eslint.org/blog/2019/08/eslint-v6.2.1-released
- https://github.com/advisories/GHSA-3gx7-xhv7-5mx3
- https://github.com/mysticatea/eslint-utils
- https://www.npmjs.com/advisories/1118
