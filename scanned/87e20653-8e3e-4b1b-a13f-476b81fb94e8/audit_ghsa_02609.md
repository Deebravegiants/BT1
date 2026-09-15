# [H] tmpl vulnerable to Inefficient Regular Expression Complexity which may lead to resource exhaustion

## Summary
Severity: High
Advisory: GHSA-jgrx-mgxx-jf9v
CVE: CVE-2021-3777
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-09-20
Source: https://github.com/advisories/GHSA-jgrx-mgxx-jf9v
Type: github-advisory

## Affected
- npm: `tmpl` — affected >=0 <1.0.5

## Details
nodejs-tmpl is simple string formatting. tmpl is vulnerable to Inefficient Regular Expression Complexity which may lead to resource exhaustion.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3777
- https://github.com/daaku/nodejs-tmpl/commit/4c654e4d1542f329ed561fd95ccd80f30c6872d6
- https://github.com/daaku/nodejs-tmpl
- https://huntr.dev/bounties/a07b547a-f457-41c9-9d89-ee48bee8a4df
