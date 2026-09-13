# [C] CVE-2016-2555

## Summary
Severity: Critical
Advisory: CVE-2016-2555
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-13
Source: https://osv.dev/vulnerability/CVE-2016-2555
Type: osv

## Details
SQL injection vulnerability in include/lib/mysql_connect.inc.php in ATutor 2.2.1 allows remote attackers to execute arbitrary SQL commands via the searchFriends function to friends.inc.php.

## References
- https://www.exploit-db.com/exploits/39514/
- http://www.rapid7.com/db/modules/exploit/multi/http/atutor_sqli
- https://github.com/atutor/ATutor/commit/629b2c992447f7670a2fecc484abfad8c4c2d298
- https://github.com/atutor/ATutor/commit/945a9dca01def8536516088da30fe6a4b7e9fa85
- http://sourceincite.com/research/src-2016-08/
