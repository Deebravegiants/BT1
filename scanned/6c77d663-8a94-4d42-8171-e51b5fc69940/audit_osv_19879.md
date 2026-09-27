# [H] CVE-2021-27230

## Summary
Severity: High
Advisory: CVE-2021-27230
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-15
Source: https://osv.dev/vulnerability/CVE-2021-27230
Type: osv

## Details
ExpressionEngine before 5.4.2 and 6.x before 6.0.3 allows PHP Code Injection by certain authenticated users who can leverage Translate::save() to write to an _lang.php file under the system/user/language directory.

## References
- http://seclists.org/fulldisclosure/2021/Mar/32
- https://expressionengine.com/features
- https://hackerone.com/reports/1093444
- http://karmainsecurity.com/KIS-2021-03
- http://packetstormsecurity.com/files/161805/ExpressionEngine-6.0.2-PHP-Code-Injection.html
