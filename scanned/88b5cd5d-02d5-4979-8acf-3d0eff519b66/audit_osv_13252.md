# [H] CVE-2018-18891

## Summary
Severity: High
Advisory: CVE-2018-18891
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-11-01
Source: https://osv.dev/vulnerability/CVE-2018-18891
Type: osv

## Details
MiniCMS 1.10 allows file deletion via /mc-admin/post.php?state=delete&delete= because the authentication check occurs too late.

## References
- https://github.com/AvaterXXX/MiniCms/blob/master/Authentication%20and%20Information%20Exposure.md#authentication-vulnerability
- https://www.patec.cn/newsshow.php?cid=24&id=135
