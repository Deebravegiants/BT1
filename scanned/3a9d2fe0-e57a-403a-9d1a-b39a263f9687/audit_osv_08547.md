# [C] CVE-2016-4344

## Summary
Severity: Critical
Advisory: CVE-2016-4344
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-22
Source: https://osv.dev/vulnerability/CVE-2016-4344
Type: osv

## Details
Integer overflow in the xml_utf8_encode function in ext/xml/xml.c in PHP before 7.0.4 allows remote attackers to cause a denial of service or possibly have unspecified other impact via a long argument to the utf8_encode function, leading to a heap-based buffer overflow.

## References
- http://php.net/ChangeLog-7.php
- http://www.openwall.com/lists/oss-security/2016/04/28/2
- https://bugs.php.net/bug.php?id=71637
