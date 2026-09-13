# [M] OS Command Injection in fsa

## Summary
Severity: Medium
Advisory: GHSA-3p94-vj97-fm4q
CVE: CVE-2020-7615
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-09
Source: https://github.com/advisories/GHSA-3p94-vj97-fm4q
Type: github-advisory

## Affected
- npm: `fsa` — affected >=0

## Details
fsa through 0.5.1 is vulnerable to Command Injection. The first argument of 'execGitCommand()', located within 'lib/rep.js#63' can be controlled by users without any sanitization to inject arbitrary commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7615
- https://github.com/gregof/fsa/blob/master/lib/rep.js#L12
- https://snyk.io/vuln/SNYK-JS-FSA-564118
