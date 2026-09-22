# [H] CVE-2017-7186

## Summary
Severity: High
Advisory: CVE-2017-7186
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-20
Source: https://osv.dev/vulnerability/CVE-2017-7186
Type: osv

## Details
libpcre1 in PCRE 8.40 and libpcre2 in PCRE2 10.23 allow remote attackers to cause a denial of service (segmentation violation for read access, and application crash) by triggering an invalid Unicode property lookup.

## References
- http://www.securityfocus.com/bid/97030
- https://access.redhat.com/errata/RHSA-2018:2486
- https://bugs.exim.org/show_bug.cgi?id=2052
- https://security.gentoo.org/glsa/201710-09
- https://security.gentoo.org/glsa/201710-25
- https://blogs.gentoo.org/ago/2017/03/14/libpcre-invalid-memory-read-in-match-pcre_exec-c/
- https://vcs.pcre.org/pcre/code/trunk/pcre_internal.h?r1=1649&r2=1688&sortby=date
- https://vcs.pcre.org/pcre/code/trunk/pcre_ucd.c?r1=1490&r2=1688&sortby=date
- https://vcs.pcre.org/pcre2/code/trunk/src/pcre2_internal.h?r1=600&r2=670&sortby=date
- https://vcs.pcre.org/pcre2/code/trunk/src/pcre2_ucd.c?r1=316&r2=670&sortby=date
