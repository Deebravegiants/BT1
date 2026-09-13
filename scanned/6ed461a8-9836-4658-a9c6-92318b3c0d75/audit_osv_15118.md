# [H] CVE-2019-13602

## Summary
Severity: High
Advisory: CVE-2019-13602
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-14
Source: https://osv.dev/vulnerability/CVE-2019-13602
Type: osv

## Details
An Integer Underflow in MP4_EIA608_Convert() in modules/demux/mp4/mp4.c in VideoLAN VLC media player through 3.0.7.1 allows remote attackers to cause a denial of service (heap-based buffer overflow and crash) or possibly have unspecified other impact via a crafted .mp4 file.

## References
- http://www.securityfocus.com/bid/109158
- https://git.videolan.org/?p=vlc.git%3Ba=commit%3Bh=8e8e0d72447f8378244f5b4a3dcde036dbeb1491
- https://git.videolan.org/?p=vlc.git%3Ba=commit%3Bh=b2b157076d9e94df34502dd8df0787deb940e938
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00037.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00040.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00081.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00036.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00046.html
- https://seclists.org/bugtraq/2019/Aug/36
- https://security.gentoo.org/glsa/201909-02
- https://usn.ubuntu.com/4074-1/
- https://www.debian.org/security/2019/dsa-4504
