# [C] Prototype Pollution in deeply

## Summary
Severity: Critical
Advisory: GHSA-8j4w-5fw4-rm27
CVE: CVE-2019-10750
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-08-27
Source: https://github.com/advisories/GHSA-8j4w-5fw4-rm27
Type: github-advisory

## Affected
- npm: `deeply` — affected >=0 <3.1.0

## Details
Versions of `deeply` prior to 1.0.1 are vulnerable to Prototype Pollution. The package fails to validate which Object properties it updates. This allows attackers to modify the prototype of Object, causing the addition or modification of an existing property on all objects.




## Recommendation

Upgrade to version 3.1.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10750
- https://snyk.io/vuln/SNYK-JS-DEEPLY-451026
- https://www.npmjs.com/advisories/1030
