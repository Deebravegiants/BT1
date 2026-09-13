# [H] Cross-Site Request Forgery (CSRF) in keystone

## Summary
Severity: High
Advisory: GHSA-q43c-g2g7-6gxj
CVE: CVE-2017-16570
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2017-11-30
Source: https://github.com/advisories/GHSA-q43c-g2g7-6gxj
Type: github-advisory

## Affected
- npm: `keystone` — affected >=0 <4.0.0-beta.7

## Details
Versions of `keystone` prior to 4.0.0 are vulnerable to Cross-Site Request Forgery (CSRF). The package fails to validate the presence of the `X-CSRF-Token` header, which may allow attackers to carry actions on behalf of other users on all endpoints.


## Recommendation

Update to version 4.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16570
- https://github.com/keystonejs/keystone/issues/4437
- https://github.com/keystonejs/keystone/pull/4478
- https://github.com/advisories/GHSA-q43c-g2g7-6gxj
- https://securelayer7.net/download/pdf/KeystoneJS-Pentest-Report-SecureLayer7.pdf
- https://snyk.io/vuln/SNYK-JS-KEYSTONE-449663
- https://www.exploit-db.com/exploits/43922
- https://www.npmjs.com/advisories/979
- http://blog.securelayer7.net/keystonejs-open-source-penetration-testing-report
