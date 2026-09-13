# [H] CVE-2017-5520

## Summary
Severity: High
Advisory: CVE-2017-5520
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-17
Source: https://osv.dev/vulnerability/CVE-2017-5520
Type: osv

## Details
The media rename feature in GeniXCMS through 0.0.8 does not consider alternative PHP file extensions when checking uploaded files for PHP content, which enables a user to rename and execute files with the `.php6`, `.php7` and `.phtml` extensions.

## References
- http://www.securityfocus.com/bid/95460
- https://github.com/semplon/GeniXCMS/issues/62
