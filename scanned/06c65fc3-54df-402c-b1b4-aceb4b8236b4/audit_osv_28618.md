# [H] CVE-2024-35584

## Summary
Severity: High
Advisory: CVE-2024-35584
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-15
Source: https://osv.dev/vulnerability/CVE-2024-35584
Type: osv

## Details
SQL injection vulnerabilities were discovered in Ajax.php, ForWindow.php, ForExport.php, Modules.php, functions/HackingLogFnc.php in OpenSis Community Edition 9.1 to 8.0, and possibly earlier versions. It is possible for an authenticated user to perform SQL Injection due to the lack to sanitisation. The application takes arbitrary value from "X-Forwarded-For" header and appends it to a SQL INSERT statement directly, leading to SQL Injection.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35584.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35584
- https://github.com/whwhwh96/CVE-2024-35584
