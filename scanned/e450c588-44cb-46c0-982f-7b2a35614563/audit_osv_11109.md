# [C] CVE-2017-6089

## Summary
Severity: Critical
Advisory: CVE-2017-6089
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-03
Source: https://osv.dev/vulnerability/CVE-2017-6089
Type: osv

## Details
SQL injection vulnerability in PhpCollab 2.5.1 and earlier allows remote attackers to execute arbitrary SQL commands via the (1) project or id parameters to topics/deletetopics.php; the (2) id parameter to bookmarks/deletebookmarks.php; or the (3) id parameter to calendar/deletecalendar.php.

## References
- https://sysdream.com/news/lab/2017-09-29-cve-2017-6089-phpcollab-2-5-1-multiple-sql-injections-unauthenticated/
- https://www.exploit-db.com/exploits/42935/
