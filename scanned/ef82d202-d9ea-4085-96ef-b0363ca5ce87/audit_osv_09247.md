# [C] CVE-2016-9138

## Summary
Severity: Critical
Advisory: CVE-2016-9138
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-04
Source: https://osv.dev/vulnerability/CVE-2016-9138
Type: osv

## Details
PHP through 5.6.27 and 7.x through 7.0.12 mishandles property modification during __wakeup processing, which allows remote attackers to cause a denial of service or possibly have unspecified other impact via crafted serialized data, as demonstrated by Exception::__toString with DateInterval::__wakeup.

## References
- http://www.securityfocus.com/bid/95268
- http://www.openwall.com/lists/oss-security/2016/11/01/2
- https://bugs.php.net/bug.php?id=73147
