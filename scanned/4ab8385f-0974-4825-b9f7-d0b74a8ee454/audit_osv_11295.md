# [H] CVE-2017-7272

## Summary
Severity: High
Advisory: CVE-2017-7272
CVSS: 7.4 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:N)
Published: 2017-03-27
Source: https://osv.dev/vulnerability/CVE-2017-7272
Type: osv

## Details
PHP through 7.1.11 enables potential SSRF in applications that accept an fsockopen or pfsockopen hostname argument with an expectation that the port number is constrained. Because a :port syntax is recognized, fsockopen will use the port number that is specified in the hostname argument, instead of the port number in the second argument of the function.

## References
- http://www.securitytracker.com/id/1038158
- https://bugs.php.net/bug.php?id=75505
- http://www.securityfocus.com/bid/97178
- https://security.netapp.com/advisory/ntap-20180112-0001/
- https://www.sec-consult.com/fxdata/seccons/prod/temedia/advisories_txt/20170403-0_PHP_Misbehavior_of_fsockopen_function_v10.txt
- https://bugs.php.net/bug.php?id=74216
- https://github.com/php/php-src/commit/bab0b99f376dac9170ac81382a5ed526938d595a
