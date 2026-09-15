# [H] CVE-2018-19898

## Summary
Severity: High
Advisory: CVE-2018-19898
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-06
Source: https://osv.dev/vulnerability/CVE-2018-19898
Type: osv

## Details
ThinkCMF X2.2.2 has SQL Injection via the method edit_post in ArticleController.class.php and is exploitable by normal authenticated users via the post[id][1] parameter in an article edit_post action.

## References
- https://github.com/thinkcmf/cmfx/issues/26
