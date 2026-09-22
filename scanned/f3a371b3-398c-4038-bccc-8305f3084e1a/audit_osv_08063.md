# [H] CVE-2016-10165

## Summary
Severity: High
Advisory: CVE-2016-10165
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2017-02-03
Source: https://osv.dev/vulnerability/CVE-2016-10165
Type: osv

## Details
The Type_MLU_Read function in cmstypes.c in Little CMS (aka lcms2) allows remote attackers to obtain sensitive information or cause a denial of service via an image with a crafted ICC profile, which triggers an out-of-bounds heap read.

## References
- http://lists.opensuse.org/opensuse-updates/2017-01/msg00174.html
- http://rhn.redhat.com/errata/RHSA-2016-2079.html
- http://rhn.redhat.com/errata/RHSA-2016-2658.html
- http://www.debian.org/security/2017/dsa-3774
- http://www.securityfocus.com/bid/95808
- http://www.securitytracker.com/id/1039596
- https://access.redhat.com/errata/RHSA-2017:2999
- https://access.redhat.com/errata/RHSA-2017:3046
- https://access.redhat.com/errata/RHSA-2017:3264
- https://access.redhat.com/errata/RHSA-2017:3267
- https://access.redhat.com/errata/RHSA-2017:3268
- https://access.redhat.com/errata/RHSA-2017:3453
- https://security.netapp.com/advisory/ntap-20171019-0001/
- https://usn.ubuntu.com/3770-1/
- https://usn.ubuntu.com/3770-2/
- http://www.openwall.com/lists/oss-security/2017/01/23/1
- http://www.openwall.com/lists/oss-security/2017/01/25/14
- http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html
- https://github.com/mm2/Little-CMS/commit/5ca71a7bc18b6897ab21d815d15e218e204581e2
