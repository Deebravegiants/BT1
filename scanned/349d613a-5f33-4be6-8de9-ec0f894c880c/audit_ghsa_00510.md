# [M] ReDoS via long string of semicolons in tough-cookie

## Summary
Severity: Medium
Advisory: GHSA-qhv9-728r-6jqg
CVE: CVE-2016-1000232
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2018-10-10
Source: https://github.com/advisories/GHSA-qhv9-728r-6jqg
Type: github-advisory

## Affected
- npm: `tough-cookie` — affected >=0 <2.3.0

## Details
Affected versions of `tough-cookie` may be vulnerable to regular expression denial of service when long strings of semicolons exist in the `Set-Cookie` header.


## Recommendation

Update to version 2.3.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000232
- https://github.com/salesforce/tough-cookie/commit/615627206357d997d5e6ff9da158997de05235ae
- https://github.com/salesforce/tough-cookie/commit/e4fc2e0f9ee1b7a818d68f0ac7ea696f377b1534
- https://access.redhat.com/errata/RHSA-2016:2101
- https://access.redhat.com/errata/RHSA-2017:2912
- https://access.redhat.com/security/cve/cve-2016-1000232
- https://github.com/advisories/GHSA-qhv9-728r-6jqg
- https://github.com/salesforce/tough-cookie
- https://www.ibm.com/blogs/psirt/ibm-security-bulletin-ibm-api-connect-is-affected-by-node-js-tough-cookie-module-vulnerability-to-a-denial-of-service-cve-2016-1000232
- https://www.npmjs.com/advisories/130
