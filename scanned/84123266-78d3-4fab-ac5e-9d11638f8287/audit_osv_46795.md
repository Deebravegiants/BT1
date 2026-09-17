# [C] CVE-2015-3210

## Summary
Severity: Critical
Advisory: CVE-2015-3210
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/CVE-2015-3210
Type: osv

## Details
Heap-based buffer overflow in PCRE 8.34 through 8.37 and PCRE2 10.10 allows remote attackers to execute arbitrary code via a crafted regular expression, as demonstrated by /^(?P=B)((?P=B)(?J:(?P<B>c)(?P<B>a(?P=B)))>WGXCREDITS)/, a different vulnerability than CVE-2015-8384.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.securityfocus.com/bid/74934
- https://access.redhat.com/errata/RHSA-2016:1132
- https://bugs.exim.org/show_bug.cgi?id=1636
- http://www.openwall.com/lists/oss-security/2015/06/01/7
- http://www.openwall.com/lists/oss-security/2015/12/02/11
- https://bugs.exim.org/show_bug.cgi?id=1636
- https://bugs.exim.org/show_bug.cgi?id=1636
- http://www.securityfocus.com/bid/74934
