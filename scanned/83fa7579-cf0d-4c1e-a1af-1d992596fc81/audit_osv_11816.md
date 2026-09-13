# [M] CVE-2017-9928

## Summary
Severity: Medium
Advisory: CVE-2017-9928
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-26
Source: https://osv.dev/vulnerability/CVE-2017-9928
Type: osv

## Details
In lrzip 0.631, a stack buffer overflow was found in the function get_fileinfo in lrzip.c:979, which allows attackers to cause a denial of service via a crafted file.

## References
- http://somevulnsofadlab.blogspot.com/2017/06/lrzipstack-buffer-overflow-in.html
- https://lists.debian.org/debian-lts-announce/2021/08/msg00001.html
- https://security.gentoo.org/glsa/202005-01
- https://github.com/ckolivas/lrzip/issues/74
