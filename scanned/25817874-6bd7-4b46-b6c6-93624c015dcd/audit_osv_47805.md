# [H] CVE-2017-12836

## Summary
Severity: High
Advisory: CVE-2017-12836
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-24
Source: https://osv.dev/vulnerability/CVE-2017-12836
Type: osv

## Details
CVS 1.12.x, when configured to use SSH for remote repositories, might allow remote attackers to execute arbitrary code via a repository URL with a crafted hostname, as demonstrated by "-oProxyCommand=id;localhost:/bar."

## References
- http://www.debian.org/security/2017/dsa-3940
- http://www.openwall.com/lists/oss-security/2017/08/11/4
- http://www.securityfocus.com/bid/100279
- http://www.ubuntu.com/usn/USN-3399-1
- https://security.gentoo.org/glsa/201709-17
- https://bugzilla.redhat.com/show_bug.cgi?id=1480800
- http://www.openwall.com/lists/oss-security/2017/08/11/1
- http://lists.nongnu.org/archive/html/bug-cvs/2017-08/msg00000.html
