# [M] CVE-2018-6942

## Summary
Severity: Medium
Advisory: CVE-2018-6942
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-13
Source: https://osv.dev/vulnerability/CVE-2018-6942
Type: osv

## Details
An issue was discovered in FreeType 2 through 2.9. A NULL pointer dereference in the Ins_GETVARIATION() function within ttinterp.c could lead to DoS via a crafted font file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00054.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=5736
- https://usn.ubuntu.com/3572-1/
- https://git.savannah.gnu.org/cgit/freetype/freetype2.git/commit/?id=29c759284e305ec428703c9a5831d0b1fc3497ef
