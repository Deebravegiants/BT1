# [H] CVE-2017-16894

## Summary
Severity: High
Advisory: CVE-2017-16894
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-11-20
Source: https://osv.dev/vulnerability/CVE-2017-16894
Type: osv

## Details
In Laravel framework through 5.5.21, remote attackers can obtain sensitive information (such as externally usable passwords) via a direct request for the /.env URI. NOTE: this CVE is only about Laravel framework's writeNewEnvironmentFileWith function in src/Illuminate/Foundation/Console/KeyGenerateCommand.php, which uses file_put_contents without restricting the .env permissions. The .env filename is not used exclusively by Laravel framework.

## References
- http://packetstormsecurity.com/files/153641/PHP-Laravel-Framework-Token-Unserialize-Remote-Command-Execution.html
- https://twitter.com/finnwea/status/967709791442341888
- http://whiteboyz.xyz/laravel-env-file-vuln.html
