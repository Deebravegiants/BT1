# [M] CVE-2016-7499

## Summary
Severity: Medium
Advisory: CVE-2016-7499
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/CVE-2016-7499
Type: osv

## Details
The sbr_make_f_master function in aacsbr.c in Libav 11.7 allows remote attackers to cause a denial of service (divide-by-zero error and application crash) via a crafted mp3 file.

## References
- https://git.libav.org/?p=libav.git%3Ba=blobdiff%3Bf=libavcodec/aacsbr.c%3Bh=7d156e525b40b197c38db17acf16730845b91e56%3Bhp=dbfb1677813ce6c531e4362d0be7ccf9fdfdd28e%3Bhb=a50a5ff29ec5a8243499769e2bb9b5509ce9fd52%3Bhpb=f55e3ff5891daf3d538b4d9176371960200d68fa
- http://www.openwall.com/lists/oss-security/2016/09/21/9
- http://www.securityfocus.com/bid/93102
- https://blogs.gentoo.org/ago/2016/09/21/libav-divide-by-zero-in-sbr_make_f_master-aacsbr-c/
