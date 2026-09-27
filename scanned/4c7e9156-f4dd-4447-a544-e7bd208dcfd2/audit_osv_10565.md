# [H] CVE-2017-17095

## Summary
Severity: High
Advisory: CVE-2017-17095
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-02
Source: https://osv.dev/vulnerability/CVE-2017-17095
Type: osv

## Details
tools/pal2rgb.c in pal2rgb in LibTIFF 4.0.9 allows remote attackers to cause a denial of service (TIFFSetupStrips heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted TIFF file.

## References
- https://lists.debian.org/debian-lts-announce/2019/11/msg00027.html
- https://usn.ubuntu.com/3606-1/
- https://www.exploit-db.com/exploits/43322/
- http://www.securityfocus.com/bid/102124
- https://security.gentoo.org/glsa/202003-25
- https://www.debian.org/security/2018/dsa-4349
- http://bugzilla.maptools.org/show_bug.cgi?id=2750
- http://www.openwall.com/lists/oss-security/2017/11/30/3
