# [H] CVE-2020-15878

## Summary
Severity: High
Advisory: CVE-2020-15878
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2020-15878
Type: osv

## Details
An issue was discovered in LibreNMS 1.65. A remote authenticated attacker with normal privileges can extract all the information from the LibreNMS database via a SQL injection in the address parameter in the /ajax_table.php API endpoint.

## References
- https://community.librenms.org/c/announcements
- https://github.com/librenms/librenms/compare/1.65...1.65.1
- https://github.com/librenms/librenms/releases/tag/1.65.1
- https://www.shielder.com/advisories/librenms-address-authenticated-sql-injection/
- https://shielder.it/blog
