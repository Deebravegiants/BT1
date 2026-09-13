# [H] CVE-2018-20796

## Summary
Severity: High
Advisory: CVE-2018-20796
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-02-26
Source: https://osv.dev/vulnerability/CVE-2018-20796
Type: osv

## Details
In the GNU C Library (aka glibc or libc6) through 2.29, check_dst_limits_calc_pos_1 in posix/regexec.c has Uncontrolled Recursion, as demonstrated by '(\227|)(\\1\\1|t1|\\\2537)+' in grep.

## References
- https://support.f5.com/csp/article/K26346590?utm_source=f5support&amp%3Butm_medium=RSS
- http://www.securityfocus.com/bid/107160
- https://security.netapp.com/advisory/ntap-20190315-0002/
- https://debbugs.gnu.org/cgi/bugreport.cgi?bug=34141
- https://lists.gnu.org/archive/html/bug-gnulib/2019-01/msg00108.html
