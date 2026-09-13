# [H] SQL injection in ChurchCRM.0

## Summary
Severity: High
Advisory: CVE-2026-39341
Aliases: GHSA-3h69-vjff-jj5c
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-39341
Type: osv

## Details
ChurchCRM is an open-source church management system. Prior to 7.1.0, the application is vulnerable to time-based SQL injection due to an improper input validation. Endpoint Reports/ConfirmReportEmail.php?familyId= is not correctly sanitising user input, specifically, the sanitised input is not used to create the SQL query. This vulnerability is fixed in 7.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39341.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-3h69-vjff-jj5c
- https://nvd.nist.gov/vuln/detail/CVE-2026-39341
