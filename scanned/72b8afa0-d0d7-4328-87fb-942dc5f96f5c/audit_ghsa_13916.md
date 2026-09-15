# [H] mt7688-wiscan is vulnerable to Command Injection due to improper input sanitization

## Summary
Severity: High
Advisory: GHSA-5h8c-8ccp-8gmh
CVE: CVE-2022-25916
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-01
Source: https://github.com/advisories/GHSA-5h8c-8ccp-8gmh
Type: github-advisory

## Affected
- npm: `mt7688-wiscan` — affected >=0 <0.8.3

## Details
Versions of the package mt7688-wiscan before 0.8.3 are vulnerable to Command Injection due to improper input sanitization in the 'wiscan.scan' function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25916
- https://github.com/simenkid/mt7688-wiscan/commit/ff6d6567c65b4e972916a8fbc4533212f20a2fa5
- https://github.com/simenkid/mt7688-wiscan
- https://github.com/simenkid/mt7688-wiscan/blob/master/index.js%23L22
- https://security.snyk.io/vuln/SNYK-JS-MT7688WISCAN-3177394
