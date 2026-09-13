# [C] CVE-2017-10682

## Summary
Severity: Critical
Advisory: CVE-2017-10682
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-29
Source: https://osv.dev/vulnerability/CVE-2017-10682
Type: osv

## Details
SQL injection vulnerability in the administrative backend in Piwigo through 2.9.1 allows remote users to execute arbitrary SQL commands via the cat_false or cat_true parameter in the comments or status page to cat_options.php.

## References
- http://www.securityfocus.com/bid/99357
- https://www.exploit-db.com/exploits/43337/
- https://github.com/Piwigo/Piwigo/commit/3dd6812412289a199564e63fffd0a9754010b9e0
- https://github.com/Piwigo/Piwigo/issues/724
