# [H] CVE-2019-5887

## Summary
Severity: High
Advisory: CVE-2019-5887
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-01-10
Source: https://osv.dev/vulnerability/CVE-2019-5887
Type: osv

## Details
An issue was discovered in ShopXO 1.2.0. In the UnlinkDir method of the FileUtil.php file, the input parameters are not checked, resulting in input mishandling by the rmdir method. Attackers can delete arbitrary files by using "../" directory traversal.

## References
- https://github.com/gongfuxiang/shopxo/issues/2
