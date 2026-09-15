# [H] CVE-2021-45078

## Summary
Severity: High
Advisory: CVE-2021-45078
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-12-15
Source: https://osv.dev/vulnerability/CVE-2021-45078
Type: osv

## Details
stab_xcoff_builtin_type in stabs.c in GNU Binutils through 2.37 allows attackers to cause a denial of service (heap-based buffer overflow) or possibly have unspecified other impact, as demonstrated by an out-of-bounds write. NOTE: this issue exists because of an incorrect fix for CVE-2018-12699.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UQBH244M5PV6S6UMHUTCVCWFZDX7Y4M6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UUHLDDT3HH7YEY6TX7IJRGPJUTNNVEL3/
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=161e87d12167b1e36193385485c1f6ce92f74f02
- https://security.gentoo.org/glsa/202208-30
- https://security.netapp.com/advisory/ntap-20220107-0002/
- https://sourceware.org/bugzilla/show_bug.cgi?id=28694
