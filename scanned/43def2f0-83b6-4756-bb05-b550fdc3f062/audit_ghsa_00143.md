# [C] Sensitive Data Exposure in msrcrypto

## Summary
Severity: Critical
Advisory: GHSA-qg3g-2mgh-33j8
CVE: CVE-2018-8319
CWE: CWE-682
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-09-10
Source: https://github.com/advisories/GHSA-qg3g-2mgh-33j8
Type: github-advisory

## Affected
- npm: `msrcrypto` — affected >=0 <1.4.1

## Details
Versions of `msrcrypto` prior to 1.4.1 are vulnerable to Sensitive Data Exposure. The package's Elliptic Curve Cryptography (ECC) implementation may leak information about a server's private ECC key. It can also allow attackers to craft invalid ECDSA signatures that pass as valid. There is no published proof-of-concept for this vulnerability.


## Recommendation

Upgrade to version 1.4.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8319
- https://github.com/advisories/GHSA-qg3g-2mgh-33j8
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8319
- https://www.npmjs.com/advisories/1112
- http://www.securityfocus.com/bid/104655
- http://www.securitytracker.com/id/1041268
