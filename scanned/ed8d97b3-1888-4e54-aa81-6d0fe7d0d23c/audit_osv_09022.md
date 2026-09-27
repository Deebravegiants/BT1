# [M] CVE-2016-7424

## Summary
Severity: Medium
Advisory: CVE-2016-7424
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-10-07
Source: https://osv.dev/vulnerability/CVE-2016-7424
Type: osv

## Details
The put_no_rnd_pixels8_xy2_mmx function in x86/rnd_template.c in libav 11.7 and earlier allows remote attackers to cause a denial of service (NULL pointer dereference and crash) via a crafted MP3 file.

## References
- http://www.securityfocus.com/bid/93038
- https://git.libav.org/?p=libav.git%3Ba=commit%3Bh=136f55207521f0b03194ef5b55ba70f1635d6aee
- http://www.debian.org/security/2016/dsa-3685
- http://www.openwall.com/lists/oss-security/2016/09/16/17
- http://www.openwall.com/lists/oss-security/2016/09/17/1
- http://www.openwall.com/lists/oss-security/2016/09/17/4
- https://blogs.gentoo.org/ago/2016/09/17/libav-null-pointer-dereference-in-put_no_rnd_pixels8_xy2_mmx-rnd_template-c/
- https://bugzilla.libav.org/show_bug.cgi?id=962
