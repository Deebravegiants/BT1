# [M] CVE-2020-15873

## Summary
Severity: Medium
Advisory: CVE-2020-15873
Aliases: GHSA-g5r6-vrmx-9gwj
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-07-21
Source: https://osv.dev/vulnerability/CVE-2020-15873
Type: osv

## Details
In LibreNMS before 1.65.1, an authenticated attacker can achieve SQL Injection via the customoid.inc.php device_id POST parameter to ajax_form.php.

## References
- https://community.librenms.org/c/announcements
- https://github.com/librenms/librenms/compare/1.65...1.65.1
- https://github.com/librenms/librenms/commit/8f3a29cde5bbd8608f9b42923a7d7e2598bcac4e
- https://github.com/librenms/librenms/pull/11923
- https://research.loginsoft.com/bugs/blind-sql-injection-in-librenms/
