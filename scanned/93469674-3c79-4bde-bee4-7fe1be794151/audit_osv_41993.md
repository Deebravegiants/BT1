# [M] Koha SQL Injection in reports/catalogue_out.pl via Filter URL Parameter

## Summary
Severity: Medium
Advisory: CVE-2026-6428
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N/E:P/AU:Y/V:C/U:Amber)
Published: 2026-06-13
Source: https://osv.dev/vulnerability/CVE-2026-6428
Type: osv

## Details
SQL Injection in reports/catalogue_out.pl in Koha Community Koha through 22.11.37, 23.x, 24.x before 24.11.16, 25.05.x before 25.05.11, 25.11.x before 25.11.05, 26.05.x before 26.05.01, and 26.11.x before 26.11.00 allows an authenticated staff user with the Reports module flag to read arbitrary data from the Koha application database via the Filter URL parameter when the Criteria parameter matches /branchcode/.

## References
- https://koha-community.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6428.json
- https://koha-community.org/security-releases/
- https://nvd.nist.gov/vuln/detail/CVE-2026-6428
- https://bugs.koha-community.org/bugzilla3/show_bug.cgi?id=42361
- https://bugs.koha-community.org/bugzilla3/attachment.cgi?id=199539
- https://gitlab.com/koha-community/Koha
