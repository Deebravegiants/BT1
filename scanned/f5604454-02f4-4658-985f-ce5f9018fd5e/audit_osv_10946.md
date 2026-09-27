# [H] CVE-2017-5345

## Summary
Severity: High
Advisory: CVE-2017-5345
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-12
Source: https://osv.dev/vulnerability/CVE-2017-5345
Type: osv

## Details
SQL injection vulnerability in inc/lib/Control/Ajax/tags-ajax.control.php in GeniXCMS 0.0.8 allows remote authenticated editors to execute arbitrary SQL commands via the term parameter to the default URI.

## References
- http://www.securityfocus.com/bid/95660
- https://github.com/semplon/GeniXCMS/commit/6e21c01d87672d81080450e6913e0093a02bfab8
- https://github.com/semplon/GeniXCMS/issues/60
