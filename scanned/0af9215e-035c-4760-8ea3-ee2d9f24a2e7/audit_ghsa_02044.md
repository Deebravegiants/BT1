# [H] Uncontrolled Resource Consumption in trim-newlines

## Summary
Severity: High
Advisory: GHSA-7p7h-4mm5-852v
CVE: CVE-2021-33623
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-07
Source: https://github.com/advisories/GHSA-7p7h-4mm5-852v
Type: github-advisory

## Affected
- npm: `trim-newlines` — affected >=0 <3.0.1
- npm: `trim-newlines` — affected >=4.0.0 <4.0.1

## Details
@rkesters/gnuplot is an easy to use node module to draw charts using gnuplot and ps2pdf. The trim-newlines package before 3.0.1 and 4.x before 4.0.1 for Node.js has an issue related to regular expression denial-of-service (ReDoS) for the `.end()` method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33623
- https://github.com/sindresorhus/trim-newlines/commit/25246c6ce5eea1c82d448998733a6302a4350d91
- https://github.com/sindresorhus/trim-newlines/commit/b10d5f4afef832b16bc56d49fc52c68cbd403869
- https://github.com/sindresorhus/trim-newlines
- https://github.com/sindresorhus/trim-newlines/releases/tag/v4.0.1
- https://lists.debian.org/debian-lts-announce/2022/12/msg00033.html
- https://security.netapp.com/advisory/ntap-20210702-0007
- https://www.npmjs.com/package/trim-newlines
