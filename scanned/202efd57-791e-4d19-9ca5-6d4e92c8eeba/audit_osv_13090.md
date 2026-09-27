# [H] CVE-2018-17341

## Summary
Severity: High
Advisory: CVE-2018-17341
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-23
Source: https://osv.dev/vulnerability/CVE-2018-17341
Type: osv

## Details
BigTree 4.2.23 on Windows, when Advanced or Simple Rewrite routing is enabled, allows remote attackers to bypass authentication via a ..\ substring, as demonstrated by a launch.php?bigtree_htaccess_url=admin/images/..\ URI.

## References
- https://github.com/bigtreecms/BigTree-CMS/issues/345
