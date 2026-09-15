# [M] dom-iterator code execution vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jrvm-mcxc-mf6m
CVE: CVE-2024-21541
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-11-13
Source: https://github.com/advisories/GHSA-jrvm-mcxc-mf6m
Type: github-advisory

## Affected
- npm: `dom-iterator` — affected >=0 <1.0.1

## Details
Versions of the package dom-iterator before 1.0.1 are vulnerable to Arbitrary Code Execution due to use of the Function constructor without complete input sanitization. Function generates a new function body and thus care must be given to ensure that the inputs to Function are not attacker-controlled. The risks involved are similar to that of allowing attacker-controlled input to reach eval.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21541
- https://github.com/matthewmueller/dom-iterator/commit/9e0e0fad5a251de5b42feb326c4204eb04080805
- https://github.com/matthewmueller/dom-iterator
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-8383166
- https://security.snyk.io/vuln/SNYK-JS-DOMITERATOR-6157199
