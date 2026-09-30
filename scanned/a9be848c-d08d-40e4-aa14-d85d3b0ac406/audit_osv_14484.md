# [H] CVE-2019-10044

## Summary
Severity: High
Advisory: CVE-2019-10044
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-03-25
Source: https://osv.dev/vulnerability/CVE-2019-10044
Type: osv

## Details
Telegram Desktop before 1.5.12 on Windows, and the Telegram applications for Android, iOS, and Linux, is vulnerable to an IDN homograph attack when displaying messages containing URLs. This occurs because the application produces a clickable link even if (for example) Latin and Cyrillic characters exist in the same domain name, and the available font has an identical representation of characters from different alphabets.

## References
- http://www.securityfocus.com/bid/107610
- https://github.com/blazeinfosec/advisories/blob/master/telegram-advisory.txt
