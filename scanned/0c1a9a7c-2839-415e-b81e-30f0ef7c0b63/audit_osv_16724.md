# [H] CVE-2019-9192

## Summary
Severity: High
Advisory: CVE-2019-9192
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-02-26
Source: https://osv.dev/vulnerability/CVE-2019-9192
Type: osv

## Details
In the GNU C Library (aka glibc or libc6) through 2.29, check_dst_limits_calc_pos_1 in posix/regexec.c has Uncontrolled Recursion, as demonstrated by '(|)(\\1\\1)*' in grep, a different issue than CVE-2018-20796. NOTE: the software maintainer disputes that this is a vulnerability because the behavior occurs only with a crafted pattern

## References
- https://support.f5.com/csp/article/K26346590?utm_source=f5support&amp%3Butm_medium=RSS
- https://sourceware.org/bugzilla/show_bug.cgi?id=24269
