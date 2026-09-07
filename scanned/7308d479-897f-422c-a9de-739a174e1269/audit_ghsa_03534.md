# [H] Denial of service in prismjs

## Summary
Severity: High
Advisory: GHSA-h4hr-7fg3-h35w
CVE: CVE-2021-23341
CWE: CWE-400
Ecosystem: npm
Published: 2021-03-01
Source: https://github.com/advisories/GHSA-h4hr-7fg3-h35w
Type: github-advisory

## Affected
- npm: `prismjs` — affected >=0 <1.23.0

## Details
The package prismjs before 1.23.0 are vulnerable to Regular Expression Denial of Service (ReDoS) via the `prism-asciidoc`, `prism-rest`, `prism-tap` and `prism-eiffel` components.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23341
- https://github.com/PrismJS/prism/issues/2583
- https://github.com/PrismJS/prism/pull/2584
- https://github.com/PrismJS/prism/commit/c2f6a64426f44497a675cb32dccb079b3eff1609
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARS-1076583
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1076582
- https://snyk.io/vuln/SNYK-JS-PRISMJS-1076581
- https://www.npmjs.com/package/prismjs
