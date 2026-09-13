# [C] Remote Code Execution in npm-groovy-lint

## Summary
Severity: Critical
Advisory: GHSA-qc22-qwm9-j8rx
CWE: CWE-20
Ecosystem: npm
Published: 2021-12-20
Source: https://github.com/advisories/GHSA-qc22-qwm9-j8rx
Type: github-advisory

## Affected
- npm: `npm-groovy-lint` — affected >=0 <9.1.0

## Details
Versions of npm-groovy-lint prior to 9.1.0 bundle vulnerable versions of the Log4j library which are subject to remote code execution via jndi rendering. As a result npm-groovy-lint prior to 9.1.0 is also vulnerable.

## References
- https://github.com/nvuillam/npm-groovy-lint/issues/194
- https://github.com/nvuillam/npm-groovy-lint/pull/195
- https://github.com/nvuillam/npm-groovy-lint/commit/0b664519019442052e0190170c2b1c5aff7d72e7
- https://github.com/advisories/GHSA-jfh8-c2jp-5v3q
- https://github.com/nvuillam/npm-groovy-lint
