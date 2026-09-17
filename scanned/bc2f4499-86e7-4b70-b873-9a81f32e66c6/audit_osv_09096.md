# [H] CVE-2016-7902

## Summary
Severity: High
Advisory: CVE-2016-7902
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-04
Source: https://osv.dev/vulnerability/CVE-2016-7902
Type: osv

## Details
Unrestricted file upload vulnerability in the fileUnzip->unzip method in Dotclear before 2.10.3 allows remote authenticated users with permissions to manage media items to execute arbitrary code by uploading a ZIP file containing a file with a crafted extension, as demonstrated by .php.txt or .php%20.

## References
- http://www.securityfocus.com/bid/93440
- https://dotclear.org/blog/post/2016/11/01/Dotclear-2.10.3
- https://hg.dotclear.org/dotclear/rev/a9db771a5a70
- http://www.openwall.com/lists/oss-security/2016/10/05/6
