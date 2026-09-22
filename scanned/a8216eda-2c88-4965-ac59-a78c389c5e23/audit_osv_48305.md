# [H] CVE-2017-6004

## Summary
Severity: High
Advisory: CVE-2017-6004
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-16
Source: https://osv.dev/vulnerability/CVE-2017-6004
Type: osv

## Details
The compile_bracket_matchingpath function in pcre_jit_compile.c in PCRE through 8.x before revision 1680 (e.g., the PHP 7.1.1 bundled version) allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted regular expression.

## References
- http://www.securityfocus.com/bid/96295
- http://www.securitytracker.com/id/1037850
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://access.redhat.com/errata/RHSA-2018:2486
- https://security.gentoo.org/glsa/201706-11
- https://bugs.exim.org/show_bug.cgi?id=2035
- https://vcs.pcre.org/pcre/code/trunk/pcre_jit_compile.c?r1=1676&r2=1680&view=patch
