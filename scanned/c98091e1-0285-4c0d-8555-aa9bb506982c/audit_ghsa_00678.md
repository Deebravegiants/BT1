# [H] datatables.net vulnerable to Prototype Pollution due to incomplete fix

## Summary
Severity: High
Advisory: GHSA-m7j4-fhg6-xf5v
CVE: CVE-2020-28458
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2020-12-17
Source: https://github.com/advisories/GHSA-m7j4-fhg6-xf5v
Type: github-advisory

## Affected
- npm: `datatables.net` — affected >=0 <1.10.22

## Details
All versions of package datatables.net are vulnerable to Prototype Pollution due to an incomplete fix for https://snyk.io/vuln/SNYK-JS-DATATABLESNET-598806.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28458
- https://github.com/DataTables/DataTablesSrc/commit/a51cbe99fd3d02aa5582f97d4af1615d11a1ea03
- https://github.com/DataTables/DataTablesSrc
- https://github.com/DataTables/Dist-DataTables/blob/master/js/jquery.dataTables.js%23L2766
- https://security.netapp.com/advisory/ntap-20240621-0006
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-1051961
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1051962
- https://snyk.io/vuln/SNYK-JS-DATATABLESNET-1016402
- https://snyk.io/vuln/SNYK-JS-DATATABLESNET-598806
