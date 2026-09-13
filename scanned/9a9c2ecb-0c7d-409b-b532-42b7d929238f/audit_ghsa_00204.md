# [C] Arbitrary Code Injection in pouchdb

## Summary
Severity: Critical
Advisory: GHSA-cgqv-x5cx-xvqh
CVE: CVE-2016-10546
CWE: CWE-94
Ecosystem: npm
Published: 2018-07-26
Source: https://github.com/advisories/GHSA-cgqv-x5cx-xvqh
Type: github-advisory

## Affected
- npm: `pouchdb` — affected >=0 <6.0.5

## Details
Affected versions of `pouchdb` do not properly sandbox the code execution engine which executes the map/reduce functions for temporary views and design documents. Under certain circumstances, an attacker could uses this to run arbitrary code on the server.


## Recommendation

Update to version 6.0.5 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10546
- https://github.com/advisories/GHSA-cgqv-x5cx-xvqh
- https://www.npmjs.com/advisories/143
