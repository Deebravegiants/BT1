# [C] Improper Certificate Validation in xmlhttprequest-ssl

## Summary
Severity: Critical
Advisory: GHSA-72mh-269x-7mh5
CVE: CVE-2021-31597
CWE: CWE-295
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-72mh-269x-7mh5
Type: github-advisory

## Affected
- npm: `xmlhttprequest-ssl` — affected >=0 <1.6.1

## Details
The xmlhttprequest-ssl package before 1.6.1 for Node.js disables SSL certificate validation by default, because rejectUnauthorized (when the property exists but is undefined) is considered to be false within the https.request function of Node.js. In other words, no certificate is ever rejected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31597
- https://github.com/mjwwit/node-XMLHttpRequest/commit/bf53329b61ca6afc5d28f6b8d2dc2e3ca740a9b2
- https://github.com/mjwwit/node-XMLHttpRequest/compare/v1.6.0...1.6.1
- https://people.kingsds.network/wesgarland/xmlhttprequest-ssl-vuln.txt
- https://security.netapp.com/advisory/ntap-20210618-0004
