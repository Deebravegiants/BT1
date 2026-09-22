# [M] confinit vulnerable to prototype pollution

## Summary
Severity: Medium
Advisory: GHSA-jgpq-g82g-6c39
CVE: CVE-2020-7638
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2020-04-07
Source: https://github.com/advisories/GHSA-jgpq-g82g-6c39
Type: github-advisory

## Affected
- npm: `confinit` — affected >=0 <0.4.0

## Details
confinit through 0.3.0 is vulnerable to Prototype Pollution.The 'setDeepProperty' function could be tricked into adding or modifying properties of 'Object.prototype' using a '__proto__' payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7638
- https://github.com/davideicardi/confinit/commit/a34e06ca5c1c8b047ef112ef188b2fe30d2a1eab
- https://snyk.io/vuln/SNYK-JS-CONFINIT-564433
