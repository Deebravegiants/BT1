# [C] CVE-2016-9941

## Summary
Severity: Critical
Advisory: CVE-2016-9941
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-31
Source: https://osv.dev/vulnerability/CVE-2016-9941
Type: osv

## Details
Heap-based buffer overflow in rfbproto.c in LibVNCClient in LibVNCServer before 0.9.11 allows remote servers to cause a denial of service (application crash) or possibly execute arbitrary code via a crafted FramebufferUpdate message containing a subrectangle outside of the client drawing area.

## References
- http://www.securityfocus.com/bid/95170
- https://github.com/LibVNC/libvncserver/releases/tag/LibVNCServer-0.9.11
- https://lists.debian.org/debian-lts-announce/2019/10/msg00042.html
- https://usn.ubuntu.com/4587-1/
- http://www.debian.org/security/2017/dsa-3753
- https://security.gentoo.org/glsa/201702-24
- https://github.com/LibVNC/libvncserver/pull/137
