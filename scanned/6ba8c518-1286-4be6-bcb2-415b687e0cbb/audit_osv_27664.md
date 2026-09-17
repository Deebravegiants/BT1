# [M] facileManager Authenticated Variable Manipulation leading to SQL Injection

## Summary
Severity: Medium
Advisory: CVE-2024-24572
Aliases: GHSA-xw34-8pj6-75gc
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-01-31
Source: https://osv.dev/vulnerability/CVE-2024-24572
Type: osv

## Details
facileManager is a modular suite of web apps built with the sysadmin in mind. In versions 4.5.0 and earlier, the $_REQUEST global array was unsafely called inside an extract() function in admin-logs.php. The PHP file fm-init.php prevents arbitrary manipulation of $_SESSION via the GET/POST parameters. However, it does not prevent manipulation of any other sensitive variables such as $search_sql. Knowing this, an authenticated user with privileges to view site logs can manipulate the search_sql
variable by appending a GET parameter search_sql in the URL. The information above means that the checks and SQL injection prevention attempts were rendered unusable.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24572.json
- https://github.com/WillyXJ/facileManager/security/advisories/GHSA-xw34-8pj6-75gc
- https://nvd.nist.gov/vuln/detail/CVE-2024-24572
- https://github.com/WillyXJ/facileManager/commit/0aa850d4b518f10143a4c675142b15caa5872877
