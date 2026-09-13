# [M] prismjs Regular Expression Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hqhp-5p83-hx96
CVE: CVE-2021-3801
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-09-20
Source: https://github.com/advisories/GHSA-hqhp-5p83-hx96
Type: github-advisory

## Affected
- npm: `prismjs` — affected >=0 <1.25.0

## Details
Prism is a syntax highlighting library. The prismjs package is vulnerable to ReDoS (regular expression denial of service). An attacker that is able to provide a crafted HTML comment as input may cause an application to consume an excessive amount of CPU.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3801
- https://github.com/prismjs/prism/commit/0ff371bb4775a131634f47d0fe85794c547232f9
- https://github.com/prismjs/prism
- https://huntr.dev/bounties/8c16ab31-6eb6-46d1-b9a4-387222fe1b8a
