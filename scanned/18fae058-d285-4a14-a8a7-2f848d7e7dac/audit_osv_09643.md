# [C] CVE-2017-1000480

## Summary
Severity: Critical
Advisory: CVE-2017-1000480
Aliases: GHSA-9m49-vhwv-422g
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-03
Source: https://osv.dev/vulnerability/CVE-2017-1000480
Type: osv

## Details
Smarty 3 before 3.1.32 is vulnerable to a PHP code injection when calling fetch() or display() functions on custom resources that does not sanitize template name.

## References
- https://lists.debian.org/debian-lts-announce/2018/01/msg00023.html
- https://lists.debian.org/debian-lts-announce/2018/02/msg00000.html
- https://github.com/smarty-php/smarty/blob/master/change_log.txt
- https://www.debian.org/security/2018/dsa-4094
