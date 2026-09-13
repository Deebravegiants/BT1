# [H] CVE-2017-5609

## Summary
Severity: High
Advisory: CVE-2017-5609
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-28
Source: https://osv.dev/vulnerability/CVE-2017-5609
Type: osv

## Details
SQL injection vulnerability in include/functions_entries.inc.php in Serendipity 2.0.5 allows remote authenticated users to execute arbitrary SQL commands via the cat parameter.

## References
- http://www.securityfocus.com/bid/95850
- https://github.com/s9y/Serendipity/releases/tag/2.1-rc1
- https://github.com/s9y/Serendipity/commit/c62d667287f2d76c81e03a740a581eb3c51249b6
