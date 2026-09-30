# [C] CVE-2016-7479

## Summary
Severity: Critical
Advisory: CVE-2016-7479
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-12
Source: https://osv.dev/vulnerability/CVE-2016-7479
Type: osv

## Details
In all versions of PHP 7, during the unserialization process, resizing the 'properties' hash table of a serialized object may lead to use-after-free. A remote attacker may exploit this bug to gain arbitrary code execution.

## References
- http://www.securitytracker.com/id/1037659
- http://blog.checkpoint.com/2016/12/27/check-point-discovers-three-zero-day-vulnerabilities-web-programming-language-php-7
- http://www.securityfocus.com/bid/95151
- https://access.redhat.com/errata/RHSA-2018:1296
- https://security.netapp.com/advisory/ntap-20180112-0001/
- https://bugs.php.net/bug.php?id=73092
- https://www.youtube.com/watch?v=LDcaPstAuPk
- http://blog.checkpoint.com/wp-content/uploads/2016/12/PHP_Technical_Report.pdf
