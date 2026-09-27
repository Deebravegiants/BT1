# [H] CVE-2017-14727

## Summary
Severity: High
Advisory: CVE-2017-14727
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-23
Source: https://osv.dev/vulnerability/CVE-2017-14727
Type: osv

## Details
logger.c in the logger plugin in WeeChat before 1.9.1 allows a crash via strftime date/time specifiers, because a buffer is not initialized.

## References
- http://www.securityfocus.com/bid/101003
- https://weechat.org/download/security/
- https://weechat.org/news/98/20170923-Version-1.9.1-security-release/
- https://github.com/weechat/weechat/commit/f105c6f0b56fb5687b2d2aedf37cb1d1b434d556
