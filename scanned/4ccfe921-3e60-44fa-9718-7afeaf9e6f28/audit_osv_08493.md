# [H] CVE-2016-3945

## Summary
Severity: High
Advisory: CVE-2016-3945
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/CVE-2016-3945
Type: osv

## Details
Multiple integer overflows in the (1) cvt_by_strip and (2) cvt_by_tile functions in the tiff2rgba tool in LibTIFF 4.0.6 and earlier, when -b mode is enabled, allow remote attackers to cause a denial of service (crash) or execute arbitrary code via a crafted TIFF image, which triggers an out-of-bounds write.

## References
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00039.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://rhn.redhat.com/errata/RHSA-2016-1546.html
- http://rhn.redhat.com/errata/RHSA-2016-1547.html
- http://www.debian.org/security/2017/dsa-3762
- http://www.openwall.com/lists/oss-security/2016/04/08/6
- http://www.securityfocus.com/bid/85960
- https://security.gentoo.org/glsa/201701-16
- http://bugzilla.maptools.org/show_bug.cgi?id=2545
- https://bugzilla.redhat.com/show_bug.cgi?id=1325093
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
