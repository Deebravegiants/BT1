# [C] CVE-2014-9911

## Summary
Severity: Critical
Advisory: CVE-2014-9911
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-04
Source: https://osv.dev/vulnerability/CVE-2014-9911
Type: osv

## Details
Stack-based buffer overflow in the ures_getByKeyWithFallback function in common/uresbund.cpp in International Components for Unicode (ICU) before 54.1 for C/C++ allows remote attackers to cause a denial of service or possibly have unspecified other impact via a crafted uloc_getDisplayName call.

## References
- http://bugs.icu-project.org/trac/changeset/35699
- http://www.openwall.com/lists/oss-security/2016/11/25/1
- http://www.securityfocus.com/bid/94520
- http://www.securitytracker.com/id/1037556
- https://bugs.php.net/bug.php?id=67397
- https://bugzilla.redhat.com/show_bug.cgi?id=1383569
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- http://www.openwall.com/lists/oss-security/2016/11/25/1
- http://bugs.icu-project.org/trac/changeset/35699
- https://bugs.php.net/bug.php?id=67397
- https://bugzilla.redhat.com/show_bug.cgi?id=1383569
- https://bugzilla.redhat.com/show_bug.cgi?id=1383569
- http://bugs.icu-project.org/trac/ticket/1089
