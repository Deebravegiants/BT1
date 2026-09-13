# [M] CVE-2016-7977

## Summary
Severity: Medium
Advisory: CVE-2016-7977
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-05-23
Source: https://osv.dev/vulnerability/CVE-2016-7977
Type: osv

## Details
Ghostscript before 9.21 might allow remote attackers to bypass the SAFER mode protection mechanism and consequently read arbitrary files via the use of the .libfile operator in a crafted postscript document.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=8abd22010eb4db0fb1b10e430d5f5d83e015ef70
- http://rhn.redhat.com/errata/RHSA-2017-0013.html
- http://rhn.redhat.com/errata/RHSA-2017-0014.html
- http://www.securityfocus.com/bid/95334
- https://security.gentoo.org/glsa/201702-31
- http://www.debian.org/security/2016/dsa-3691
- http://www.oracle.com/technetwork/security-advisory/cpujan2018-3236628.html
- https://ghostscript.com/doc/9.21/History9.htm
- http://www.openwall.com/lists/oss-security/2016/09/29/28
- http://www.openwall.com/lists/oss-security/2016/10/05/15
- https://bugs.ghostscript.com/show_bug.cgi?id=697169
