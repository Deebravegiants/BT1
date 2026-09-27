# [H] Prototype Pollution

## Summary
Severity: High
Advisory: GHSA-6pq3-928q-x6w6
CVE: CVE-2020-8147
CWE: CWE-471
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-6pq3-928q-x6w6
Type: github-advisory

## Affected
- npm: `utils-extend` — affected >=0.0.0

## Details
All versions of `utils-extend` are vulnerable to prototype pollution. The `extend` function does not restrict the modification of an Object's prototype, which may allow an attacker to add or modify an existing property that will exist on all objects.

## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8147
- https://hackerone.com/reports/801522
- https://www.npmjs.com/advisories/1502
