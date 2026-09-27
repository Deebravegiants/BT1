# [H] CVE-2015-3217

## Summary
Severity: High
Advisory: CVE-2015-3217
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/CVE-2015-3217
Type: osv

## Details
PCRE 7.8 and 8.32 through 8.37, and PCRE2 10.10 mishandle group empty matches, which might allow remote attackers to cause a denial of service (stack-based buffer overflow) via a crafted regular expression, as demonstrated by /^(?:(?(1)\\.|([^\\\\W_])?)+)+$/.

## References
- http://rhn.redhat.com/errata/RHSA-2016-1025.html
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www-01.ibm.com/support/docview.wss?uid=isg3T1023886
- http://www.securityfocus.com/bid/75018
- https://access.redhat.com/errata/RHSA-2016:1132
- https://bugs.exim.org/show_bug.cgi?id=1638
- http://www.openwall.com/lists/oss-security/2015/06/03/7
- https://bugs.exim.org/show_bug.cgi?id=1638
- http://vcs.pcre.org/pcre?view=revision&revision=1566
- https://bugs.exim.org/show_bug.cgi?id=1638
- https://bugzilla.redhat.com/show_bug.cgi?id=1228283
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
