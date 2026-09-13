# [C] PaginationServiceProvider SQL Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-ww43-mcvh-35p4
CVE: CVE-2014-125029
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-08
Source: https://github.com/advisories/GHSA-ww43-mcvh-35p4
Type: github-advisory

## Affected
- Packagist: `ttskch/pagination-service-provider` — affected >=0 <1.0.0

## Details
A vulnerability was found in ttskch PaginationServiceProvider up to 0.x. It has been declared as critical. This vulnerability affects unknown code of the file `demo/index.php` of the component demo. The manipulation of the argument sort/id leads to sql injection. Upgrading to version 1.0.0 can address this issue. The name of the patch is 619de478efce17ece1a3b913ab16e40651e1ea7b. It is recommended to upgrade the affected component. VDB-217150 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-125029
- https://github.com/ttskch/PaginationServiceProvider/commit/619de478efce17ece1a3b913ab16e40651e1ea7b
- https://github.com/ttskch/PaginationServiceProvider
- https://github.com/ttskch/PaginationServiceProvider/releases/tag/1.0.0
- https://vuldb.com/?ctiid.217150
- https://vuldb.com/?id.217150
