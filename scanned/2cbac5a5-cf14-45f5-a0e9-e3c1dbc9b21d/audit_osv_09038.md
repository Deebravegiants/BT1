# [H] CVE-2016-7508

## Summary
Severity: High
Advisory: CVE-2016-7508
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-21
Source: https://osv.dev/vulnerability/CVE-2016-7508
Type: osv

## Details
Multiple SQL injection vulnerabilities in GLPI 0.90.4 allow an authenticated remote attacker to execute arbitrary SQL commands by using a certain character when the database is configured to use Big5 Asian encoding.

## References
- https://www.exploit-db.com/exploits/42262/
- https://github.com/glpi-project/glpi/issues/1047
