# [C] CVE-2019-10231

## Summary
Severity: Critical
Advisory: CVE-2019-10231
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-27
Source: https://osv.dev/vulnerability/CVE-2019-10231
Type: osv

## Details
Teclib GLPI before 9.4.1.1 is affected by a PHP type juggling vulnerability allowing bypass of authentication. This occurs in Auth::checkPassword() (inc/auth.class.php).

## References
- https://github.com/glpi-project/glpi/releases/tag/9.4.1.1
- https://github.com/glpi-project/glpi/pull/5520
