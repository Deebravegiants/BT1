# [C] CVE-2015-5073

## Summary
Severity: Critical
Advisory: CVE-2015-5073
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/CVE-2015-5073
Type: osv

## Details
Heap-based buffer overflow in the find_fixedlength function in pcre_compile.c in PCRE before 8.38 allows remote attackers to cause a denial of service (crash) or obtain sensitive information from heap memory and possibly bypass the ASLR protection mechanism via a crafted regular expression with an excess closing parenthesis.

## References
- http://rhn.redhat.com/errata/RHSA-2016-1025.html
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://vcs.pcre.org/pcre/code/trunk/ChangeLog?revision=1609&view=markup
- http://vcs.pcre.org/pcre?view=revision&revision=1571
- http://www-01.ibm.com/support/docview.wss?uid=isg3T1023886
- http://www.securityfocus.com/bid/75430
- http://www.securitytracker.com/id/1033154
- https://access.redhat.com/errata/RHSA-2016:1132
- https://security.gentoo.org/glsa/201607-02
- http://www.openwall.com/lists/oss-security/2015/06/26/1
- http://www.openwall.com/lists/oss-security/2015/06/26/3
- http://vcs.pcre.org/pcre?view=revision&revision=1571
- https://bugs.exim.org/show_bug.cgi?id=1651
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
