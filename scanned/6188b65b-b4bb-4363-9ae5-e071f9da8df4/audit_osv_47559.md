# [C] CVE-2016-7979

## Summary
Severity: Critical
Advisory: CVE-2016-7979
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-23
Source: https://osv.dev/vulnerability/CVE-2016-7979
Type: osv

## Details
Ghostscript before 9.21 might allow remote attackers to bypass the SAFER mode protection mechanism and consequently execute arbitrary code by leveraging type confusion in .initialize_dsc_parser.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Bh=875a0095f37626a721c7ff57d606a0f95af03913
- http://www.debian.org/security/2016/dsa-3691
- http://www.securityfocus.com/bid/95337
- https://security.gentoo.org/glsa/201702-31
- http://rhn.redhat.com/errata/RHSA-2017-0013.html
- http://rhn.redhat.com/errata/RHSA-2017-0014.html
- http://www.openwall.com/lists/oss-security/2016/10/05/15
- https://bugs.ghostscript.com/show_bug.cgi?id=697190
