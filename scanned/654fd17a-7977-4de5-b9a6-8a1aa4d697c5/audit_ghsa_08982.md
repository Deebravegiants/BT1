# [M] Concrete CMS is Vulnerable to Reflected XSS in Legacy Pagination

## Summary
Severity: Medium
Advisory: GHSA-f73j-pm2c-rxvr
CVE: CVE-2026-8245
CWE: CWE-83
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-22
Source: https://github.com/advisories/GHSA-f73j-pm2c-rxvr
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.5.1

## Details
Concrete CMS 9.5.0 and below is vulnerable to Reflected XSS in Legacy Pagination via HTML attribute injection. Concrete\Core\Legacy\Pagination builds pagination links by raw-interpolating its $URL field into href="" (<a href="{$linkURL}" …>). Any authenticated admin or report viewer with access to `/dashboard/reports/forms/legacy` who clicks the crafted URL fires the payload in their session.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8245
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/951-release-notes
- https://github.com/concretecms/concretecms
