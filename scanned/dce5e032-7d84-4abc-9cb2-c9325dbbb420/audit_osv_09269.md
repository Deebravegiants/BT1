# [C] CVE-2016-9288

## Summary
Severity: Critical
Advisory: CVE-2016-9288
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-11-11
Source: https://osv.dev/vulnerability/CVE-2016-9288
Type: osv

## Details
In framework/modules/navigation/controllers/navigationController.php in Exponent CMS v2.4.0 or older, the parameter "target" of function "DragnDropReRank" is directly used without any filtration which caused SQL injection. The payload can be used like this: /navigation/DragnDropReRank/target/1.

## References
- http://www.securitytracker.com/id/1037280
- http://www.securityfocus.com/bid/94296
- https://github.com/exponentcms/exponent-cms/commit/2ddffb2e7eafe4830e3483a4b437873022c461ba
