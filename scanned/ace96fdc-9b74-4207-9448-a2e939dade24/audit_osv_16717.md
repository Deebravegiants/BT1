# [C] CVE-2019-9169

## Summary
Severity: Critical
Advisory: CVE-2019-9169
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-26
Source: https://osv.dev/vulnerability/CVE-2019-9169
Type: osv

## Details
In the GNU C Library (aka glibc or libc6) through 2.29, proceed_next_node in posix/regexec.c has a heap-based buffer over-read via an attempted case-insensitive regular-expression match.

## References
- http://www.securityfocus.com/bid/107160
- https://sourceware.org/git/gitweb.cgi?p=glibc.git%3Ba=commit%3Bh=583dd860d5b833037175247230a328f0050dbfe9
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://kc.mcafee.com/corporate/index?page=content&id=SB10278
- https://security.gentoo.org/glsa/202006-04
- https://support.f5.com/csp/article/K54823184
- https://usn.ubuntu.com/4416-1/
- https://security.netapp.com/advisory/ntap-20190315-0002/
- https://sourceware.org/bugzilla/show_bug.cgi?id=24114
- https://debbugs.gnu.org/cgi/bugreport.cgi?bug=34140
- https://debbugs.gnu.org/cgi/bugreport.cgi?bug=34142
