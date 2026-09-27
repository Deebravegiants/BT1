# [H] CVE-2020-35701

## Summary
Severity: High
Advisory: CVE-2020-35701
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-11
Source: https://osv.dev/vulnerability/CVE-2020-35701
Type: osv

## Details
An issue was discovered in Cacti 1.2.x through 1.2.16. A SQL injection vulnerability in data_debug.php allows remote authenticated attackers to execute arbitrary SQL commands via the site_id parameter. This can lead to remote code execution.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6DDD22Z56THHDTXAFM447UH3BVINURIF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/C7DPUWZBAMCXFKAKUAJSHL3CKTOLGAK6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NBKBR2MFZJ6C2I4I5PCRR6UERPY24XZN/
- https://github.com/Cacti/cacti/issues/4022
- https://security.gentoo.org/glsa/202101-31
- https://asaf.me/2020/12/15/cacti-1-2-0-to-1-2-16-sql-injection/
