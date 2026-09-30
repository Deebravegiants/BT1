# [H] Authentication Weakness in keystone

## Summary
Severity: High
Advisory: GHSA-39pj-gq8q-9pfj
CVE: CVE-2015-9240
CWE: CWE-1255
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-06-07
Source: https://github.com/advisories/GHSA-39pj-gq8q-9pfj
Type: github-advisory

## Affected
- npm: `keystone` — affected >=0 <0.3.16

## Details
Versions of `keystone` prior to 0.3.16 are affected by a partial authentication bypass vulnerability. In the default sign in functionality, if an attacker provides a full and correct password, yet only provides part of the associated email address, authentication will be granted.


## Recommendation

Update to version 0.3.16 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-9240
- https://github.com/advisories/GHSA-39pj-gq8q-9pfj
- https://www.npmjs.com/advisories/60
- https://www.npmjs.com/package/keystone
