# [M] CVE-2024-43018

## Summary
Severity: Medium
Advisory: CVE-2024-43018
CVSS: 6.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-07-29
Source: https://osv.dev/vulnerability/CVE-2024-43018
Type: osv

## Details
Piwigo 13.8.0 and below is vulnerable to SQL Injection in the parameters max_level and min_register. These parameters are used in ws_user_gerList function from file include\ws_functions\pwg.users.php and this same function is called by ws.php file at some point can be used for searching users in advanced way in /admin.php?page=user_list.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43018.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43018
- https://github.com/Piwigo/Piwigo/issues/2197
- https://github.com/inesmarcal/CVE-2024-43018
- https://github.com/joaosilva21/CVE-2024-43018
