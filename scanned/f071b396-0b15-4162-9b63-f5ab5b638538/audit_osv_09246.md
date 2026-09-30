# [C] CVE-2016-9137

## Summary
Severity: Critical
Advisory: CVE-2016-9137
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-04
Source: https://osv.dev/vulnerability/CVE-2016-9137
Type: osv

## Details
Use-after-free vulnerability in the CURLFile implementation in ext/curl/curl_file.c in PHP before 5.6.27 and 7.x before 7.0.12 allows remote attackers to cause a denial of service or possibly have unspecified other impact via crafted serialized data that is mishandled during __wakeup processing.

## References
- http://git.php.net/?p=php-src.git%3Ba=commit%3Bh=0e6fe3a4c96be2d3e88389a5776f878021b4c59f
- https://www.tenable.com/security/tns-2016-19
- http://www.debian.org/security/2016/dsa-3698
- http://www.openwall.com/lists/oss-security/2016/11/01/2
- http://www.php.net/ChangeLog-5.php
- http://www.php.net/ChangeLog-7.php
- http://www.securityfocus.com/bid/93577
- https://bugs.php.net/bug.php?id=73147
