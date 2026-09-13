# [H] CVE-2016-7478

## Summary
Severity: High
Advisory: CVE-2016-7478
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-11
Source: https://osv.dev/vulnerability/CVE-2016-7478
Type: osv

## Details
Zend/zend_exceptions.c in PHP, possibly 5.x before 5.6.28 and 7.x before 7.0.13, allows remote attackers to cause a denial of service (infinite loop) via a crafted Exception object in serialized data, a related issue to CVE-2015-8876.

## References
- http://www.securityfocus.com/bid/95150
- https://www.youtube.com/watch?v=LDcaPstAuPk
- http://blog.checkpoint.com/2016/12/27/check-point-discovers-three-zero-day-vulnerabilities-web-programming-language-php-7
- http://blog.checkpoint.com/wp-content/uploads/2016/12/PHP_Technical_Report.pdf
- https://security.netapp.com/advisory/ntap-20180112-0001/
- https://bugs.php.net/bug.php?id=73093
