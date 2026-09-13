# [H] Missing Encryption of Sensitive Data in yarn

## Summary
Severity: High
Advisory: GHSA-wqfc-cr59-h64p
CVE: CVE-2019-5448
CWE: CWE-311, CWE-319
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-07-31
Source: https://github.com/advisories/GHSA-wqfc-cr59-h64p
Type: github-advisory

## Affected
- npm: `yarn` — affected >=0 <1.17.3

## Details
Yarn before 1.17.3 is vulnerable to Missing Encryption of Sensitive Data due to HTTP URLs in lockfile causing unencrypted authentication data to be sent over the network.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5448
- https://hackerone.com/reports/640904
- https://github.com/ChALkeR/notes/blob/master/Yarn-vuln.md
- https://yarnpkg.com/blog/2019/07/12/recommended-security-update
