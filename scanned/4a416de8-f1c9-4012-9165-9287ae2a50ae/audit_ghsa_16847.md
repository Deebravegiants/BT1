# [H] LibreNMS vulnerable to SQL injection time-based leads to database extraction

## Summary
Severity: High
Advisory: GHSA-cwx6-cx7x-4q34
CVE: CVE-2024-32461
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-22
Source: https://github.com/advisories/GHSA-cwx6-cx7x-4q34
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <24.4.0

## Details
### Summary
SQL injection vulnerability in POST /search/search=packages in LibreNMS 24.3.0 allows a user with global read privileges to execute SQL commands via the package parameter. 

### Details
There is a lack of hygiene of data coming from the user in line 83 of the file librenms/includes/html/pages/search/packages.inc.php
![vulnerability](https://github.com/librenms/librenms/assets/58785171/3ad76f72-e62b-475e-84a0-4024e751f44c)

### PoC
https://doc.clickup.com/9013166444/p/h/8ckm0bc-53/16811991bb5fff6

### Impact
With this vulnerability, we can exploit a SQL injection time based vulnerability to extract all data from the database, such as administrator credentials

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-cwx6-cx7x-4q34
- https://nvd.nist.gov/vuln/detail/CVE-2024-32461
- https://github.com/librenms/librenms/commit/d29201fce134347f891102699fbde7070debee33
- https://doc.clickup.com/9013166444/p/h/8ckm0bc-53/16811991bb5fff6
- https://github.com/librenms/librenms
