# [C] CVE-2016-1283

## Summary
Severity: Critical
Advisory: CVE-2016-1283
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-01-03
Source: https://osv.dev/vulnerability/CVE-2016-1283
Type: osv

## Details
The pcre_compile2 function in pcre_compile.c in PCRE 8.38 mishandles the /((?:F?+(?:^(?(R)a+\"){99}-))(?J)(?'R'(?'R'<((?'RR'(?'R'\){97)?J)?J)(?'R'(?'R'\){99|(:(?|(?'R')(\k'R')|((?'R')))H'R'R)(H'R))))))/ pattern and related patterns with named subgroups, which allows remote attackers to cause a denial of service (heap-based buffer overflow) or possibly have unspecified other impact via a crafted regular expression, as demonstrated by a JavaScript RegExp object encountered by Konqueror.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/178193.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/178955.html
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
- http://www.securityfocus.com/bid/79825
- http://www.securitytracker.com/id/1034555
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2016&m=slackware-security.343110
- https://access.redhat.com/errata/RHSA-2016:1132
- https://security.gentoo.org/glsa/201607-02
- https://www.tenable.com/security/tns-2016-18
- https://www.tenable.com/security/tns-2017-14
- https://bto.bluecoat.com/security-advisory/sa128
- https://bugs.exim.org/show_bug.cgi?id=1767
