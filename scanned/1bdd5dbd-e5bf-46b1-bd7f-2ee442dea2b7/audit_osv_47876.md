# [H] CVE-2017-14160

## Summary
Severity: High
Advisory: CVE-2017-14160
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/CVE-2017-14160
Type: osv

## Details
The bark_noise_hybridmp function in psy.c in Xiph.Org libvorbis 1.3.5 allows remote attackers to cause a denial of service (out-of-bounds access and application crash) or possibly have unspecified other impact via a crafted mp4 file.

## References
- https://lists.debian.org/debian-lts-announce/2019/11/msg00031.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00023.html
- https://security.gentoo.org/glsa/202003-36
- http://openwall.com/lists/oss-security/2017/09/21/2
- http://www.securityfocus.com/bid/101045
