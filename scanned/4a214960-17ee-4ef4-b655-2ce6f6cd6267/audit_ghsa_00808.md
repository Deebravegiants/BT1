# [C] Prototype Pollution in express-fileupload

## Summary
Severity: Critical
Advisory: GHSA-9wcg-jrwf-8gg7
CVE: CVE-2020-7699
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-08-05
Source: https://github.com/advisories/GHSA-9wcg-jrwf-8gg7
Type: github-advisory

## Affected
- npm: `express-fileupload` — affected >=0 <1.1.9

## Details
This affects the package express-fileupload before 1.1.8. If the parseNested option is enabled, sending a corrupt HTTP request can lead to denial of service or arbitrary code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7699
- https://github.com/richardgirges/express-fileupload/issues/236
- https://github.com/richardgirges/express-fileupload/pull/237
- https://github.com/richardgirges/express-fileupload/commit/db495357d7557ceb5c034de91a7a574bd12f9b9f
- https://github.com/richardgirges/express-fileupload
- https://security.netapp.com/advisory/ntap-20200821-0003
- https://snyk.io/vuln/SNYK-JS-EXPRESSFILEUPLOAD-595969
