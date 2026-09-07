# [M] eivindfjeldstad-dot contains prototype pollution vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wfwq-xc57-fq7v
CVE: CVE-2020-7639
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-05-25
Source: https://github.com/advisories/GHSA-wfwq-xc57-fq7v
Type: github-advisory

## Affected
- npm: `@eivifj/dot` — affected >=0 <1.0.3

## Details
eivindfjeldstad-dot below 1.0.3 is vulnerable to Prototype Pollution.The function 'set' could be tricked into adding or modifying properties of 'Object.prototype' using a '__proto__' payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7639
- https://github.com/eivindfjeldstad/dot/commit/774e4b0c97ca35d2ae40df2cd14428d37dd07a0b
- https://github.com/eivindfjeldstad/dot
- https://snyk.io/vuln/SNYK-JS-EIVIFJDOT-564435
