# [M] CVE-2016-4493

## Summary
Severity: Medium
Advisory: CVE-2016-4493
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-24
Source: https://osv.dev/vulnerability/CVE-2016-4493
Type: osv

## Details
The demangle_template_value_parm and do_hpacc_template_literal functions in cplus-dem.c in libiberty allow remote attackers to cause a denial of service (out-of-bounds read and crash) via a crafted binary.

## References
- http://www.openwall.com/lists/oss-security/2016/05/05/5
- https://gcc.gnu.org/ml/gcc-patches/2016-05/msg00223.html
- http://www.openwall.com/lists/oss-security/2016/05/05/5
- http://www.openwall.com/lists/oss-security/2016/05/05/5
- https://gcc.gnu.org/ml/gcc-patches/2016-05/msg00223.html
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=70926
- http://www.securityfocus.com/bid/90014
