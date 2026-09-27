# [H] CVE-2019-7580

## Summary
Severity: High
Advisory: CVE-2019-7580
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-07
Source: https://osv.dev/vulnerability/CVE-2019-7580
Type: osv

## Details
ThinkCMF 5.0.190111 allows remote attackers to execute arbitrary PHP code via the portal/admin_category/addpost.html alias parameter because the mishandling of a single quote character allows data/conf/route.php injection.

## References
- https://github.com/shadowsock5/ThinkCMF-5.0.190111/blob/master/README.md
- https://xz.aliyun.com/t/3997
