# [H] CVE-2014-9862

## Summary
Severity: High
Advisory: CVE-2014-9862
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-07-22
Source: https://osv.dev/vulnerability/CVE-2014-9862
Type: osv

## Details
Integer signedness error in bspatch.c in bspatch in bsdiff, as used in Apple OS X before 10.11.6 and other products, allows remote attackers to execute arbitrary code or cause a denial of service (heap-based buffer overflow) via a crafted patch file.

## References
- http://lists.apple.com/archives/security-announce/2016/Jul/msg00000.html
- https://security.FreeBSD.org/advisories/FreeBSD-SA-16:25.bspatch.asc
- https://security.gentoo.org/glsa/202003-44
- https://support.apple.com/HT206903
- http://lists.apple.com/archives/security-announce/2016/Jul/msg00000.html
- https://android.googlesource.com/platform/external/bsdiff/+/4d054795b673855e3a7556c6f2f7ab99ca509998
- https://bugs.chromium.org/p/chromium/issues/detail?id=372525
- https://chromium.googlesource.com/chromiumos/third_party/bsdiff/+/d0307d1711bd74e51b783a49f9160775aa22e659
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00026.html
- http://seclists.org/fulldisclosure/2020/Jul/8
- http://www.openwall.com/lists/oss-security/2020/07/09/2
- http://www.securityfocus.com/bid/91824
- http://www.securitytracker.com/id/1036438
- https://lists.debian.org/debian-lts-announce/2019/11/msg00028.html
- https://usn.ubuntu.com/4500-1/
