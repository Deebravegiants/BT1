# [C] CVE-2016-3132

## Summary
Severity: Critical
Advisory: CVE-2016-3132
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-3132
Type: osv

## Details
Double free vulnerability in the SplDoublyLinkedList::offsetSet function in ext/spl/spl_dllist.c in PHP 7.x before 7.0.6 allows remote attackers to execute arbitrary code via a crafted index.

## References
- http://www.securityfocus.com/bid/92356
- https://security-tracker.debian.org/tracker/CVE-2016-3132
- http://github.com/php/php-src/commit/28a6ed9f9a36b9c517e4a8a429baf4dd382fc5d5?w=1
- https://php.net/ChangeLog-7.php
- https://bugs.php.net/bug.php?id=71735
