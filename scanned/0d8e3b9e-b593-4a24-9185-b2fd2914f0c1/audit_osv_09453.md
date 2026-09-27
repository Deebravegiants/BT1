# [H] CVE-2016-9920

## Summary
Severity: High
Advisory: CVE-2016-9920
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-08
Source: https://osv.dev/vulnerability/CVE-2016-9920
Type: osv

## Details
steps/mail/sendmail.inc in Roundcube before 1.1.7 and 1.2.x before 1.2.3, when no SMTP server is configured and the sendmail program is enabled, does not properly restrict the use of custom envelope-from addresses on the sendmail command line, which allows remote authenticated users to execute arbitrary code via a modified HTTP request that sends a crafted e-mail message.

## References
- http://www.securityfocus.com/bid/94858
- http://www.openwall.com/lists/oss-security/2016/12/08/10
- https://roundcube.net/news/2016/11/28/updates-1.2.3-and-1.1.7-released
- https://security.gentoo.org/glsa/201612-44
- https://blog.ripstech.com/2016/roundcube-command-execution-via-email/
