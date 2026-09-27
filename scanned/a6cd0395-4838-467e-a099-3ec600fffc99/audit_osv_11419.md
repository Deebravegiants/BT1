# [C] CVE-2017-7695

## Summary
Severity: Critical
Advisory: CVE-2017-7695
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-11
Source: https://osv.dev/vulnerability/CVE-2017-7695
Type: osv

## Details
Unrestricted File Upload exists in BigTree CMS before 4.2.17: if an attacker uploads an 'xxx.php[space]' file, they could bypass a safety check and execute any code.

## References
- https://github.com/bigtreecms/BigTree-CMS/commit/8cf4212ea40e1b843e1aecf4b24681b0964ec04c
- https://github.com/bigtreecms/BigTree-CMS/issues/276
- http://www.math1as.com/bigtree_upload.txt
