# [M] CVE-2016-4491

## Summary
Severity: Medium
Advisory: CVE-2016-4491
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-24
Source: https://osv.dev/vulnerability/CVE-2016-4491
Type: osv

## Details
The d_print_comp function in cp-demangle.c in libiberty allows remote attackers to cause a denial of service (segmentation fault and crash) via a crafted binary, which triggers infinite recursion and a buffer overflow, related to a node having "itself as ancestor more than once."

## References
- http://www.openwall.com/lists/oss-security/2016/05/05/5
- https://gcc.gnu.org/ml/gcc-patches/2016-05/msg00105.html
- http://www.openwall.com/lists/oss-security/2016/05/05/5
- http://www.openwall.com/lists/oss-security/2016/05/05/5
- https://gcc.gnu.org/ml/gcc-patches/2016-05/msg00105.html
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=70909
- http://www.securityfocus.com/bid/90016
