# [H] CVE-2018-13049

## Summary
Severity: High
Advisory: CVE-2018-13049
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-02
Source: https://osv.dev/vulnerability/CVE-2018-13049
Type: osv

## Details
The constructSQL function in inc/search.class.php in GLPI 9.2.x through 9.3.0 allows SQL Injection, as demonstrated by triggering a crafted LIMIT clause to front/computer.php.

## References
- https://github.com/glpi-project/glpi/issues/4270
