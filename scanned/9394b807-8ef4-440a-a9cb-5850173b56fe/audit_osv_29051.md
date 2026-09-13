# [H] ChurchCRM SQL Injection Vulnerability

## Summary
Severity: High
Advisory: CVE-2024-39304
Aliases: GHSA-2rh6-gr3h-83j9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-26
Source: https://osv.dev/vulnerability/CVE-2024-39304
Type: osv

## Details
ChurchCRM is an open-source church management system. Versions of the application prior to 5.9.2 are vulnerable to an authenticated SQL injection due to an improper sanitization of user input. Authentication is required, but no elevated privileges are necessary. This allows attackers to inject SQL statements directly into the database query due to inadequate sanitization of the EID parameter in in a GET request to `/GetText.php`. Version 5.9.2 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39304.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-2rh6-gr3h-83j9
- https://nvd.nist.gov/vuln/detail/CVE-2024-39304
- https://github.com/ChurchCRM/CRM/commit/e3bd7bfbf33f01148df0ef1acdb0cf2c2b878b08
