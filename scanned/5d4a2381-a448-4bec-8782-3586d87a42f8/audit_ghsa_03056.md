# [H] Path traversal in pimcore/pimcore

## Summary
Severity: High
Advisory: GHSA-h7f9-cvh5-qw7f
CVE: CVE-2021-23340
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2021-02-25
Source: https://github.com/advisories/GHSA-h7f9-cvh5-qw7f
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <6.8.8

## Details
This affects the package pimcore/pimcore before 6.8.8. A Local FIle Inclusion vulnerability exists in the downloadCsvAction function of the CustomReportController class (bundles/AdminBundle/Controller/Reports/CustomReportController.php). An authenticated user can reach this function with a GET request at the following endpoint: /admin/reports/custom-report/download-csv?exportFile=&91;filename]. Since exportFile variable is not sanitized, an attacker can exploit a local file inclusion vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23340
- https://github.com/pimcore/pimcore/commit/1786bdd4962ee51544fad537352c2b4223309442
- https://github.com/pimcore/pimcore/blob/v6.7.2/bundles/AdminBundle/Controller/Reports/CustomReportController.php%23L454
- https://snyk.io/vuln/SNYK-PHP-PIMCOREPIMCORE-1070132
