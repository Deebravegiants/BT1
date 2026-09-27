# [C] CVE-2016-3191

## Summary
Severity: Critical
Advisory: CVE-2016-3191
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-03-17
Source: https://osv.dev/vulnerability/CVE-2016-3191
Type: osv

## Details
The compile_branch function in pcre_compile.c in PCRE 8.x before 8.39 and pcre2_compile.c in PCRE2 before 10.22 mishandles patterns containing an (*ACCEPT) substring in conjunction with nested parentheses, which allows remote attackers to execute arbitrary code or cause a denial of service (stack-based buffer overflow) via a crafted regular expression, as demonstrated by a JavaScript RegExp object encountered by Konqueror, aka ZDI-CAN-3542.

## References
- http://vcs.pcre.org/pcre2?view=revision&revision=489
- http://vcs.pcre.org/pcre?view=revision&revision=1631
- http://www-01.ibm.com/support/docview.wss?uid=isg3T1023886
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.securityfocus.com/bid/84810
- https://bugs.debian.org/815920
- https://bugs.debian.org/815921
- https://www.tenable.com/security/tns-2016-18
- http://rhn.redhat.com/errata/RHSA-2016-1025.html
- https://access.redhat.com/errata/RHSA-2016:1132
- https://bto.bluecoat.com/security-advisory/sa128
- https://bugzilla.redhat.com/show_bug.cgi?id=1311503
- https://bugs.exim.org/show_bug.cgi?id=1791
