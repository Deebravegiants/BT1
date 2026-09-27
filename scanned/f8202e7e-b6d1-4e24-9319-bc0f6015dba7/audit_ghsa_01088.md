# [M] Sensitive Data Exposure in ibm_db

## Summary
Severity: Medium
Advisory: GHSA-p77h-hv6g-fmfp
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-p77h-hv6g-fmfp
Type: github-advisory

## Affected
- npm: `ibm_db` — affected >=0 <2.6.0

## Details
Versions of `ibm_db` prior to 2.6.0 are vulnerable to Sensitive Data Exposure. The package printed database credentials in plaintext in logs while in debug mode.


## Recommendation

Upgrade to version 2.6.0 or later and ensure sensitive information was not logged.

## References
- https://github.com/ibmdb/node-ibm_db/issues/563
- https://github.com/ibmdb/node-ibm_db/commit/526c88b5eedc605274def65405279f6708d91ce8
- https://github.com/ibmdb/node-ibm_db
- https://snyk.io/vuln/SNYK-JS-IBMDB-459762
- https://www.npmjs.com/advisories/1185
