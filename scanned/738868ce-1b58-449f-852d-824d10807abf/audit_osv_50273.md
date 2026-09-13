# [C] CVE-2020-10018

## Summary
Severity: Critical
Advisory: CVE-2020-10018
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-02
Source: https://osv.dev/vulnerability/CVE-2020-10018
Type: osv

## Details
WebKitGTK through 2.26.4 and WPE WebKit through 2.26.4 (which are the versions right before 2.28.0) contains a memory corruption issue (use-after-free) that may lead to arbitrary code execution. This issue has been fixed in 2.28.0 with improved memory handling.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GLERWAS2LL7SX2GHA2DDZ2PL3QC5OHIF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DOR5LPL4UASVAR76EIHCL4O2KGDWGC6K/
- https://wpewebkit.org/security/WSA-2020-0003.html
- https://www.debian.org/security/2020/dsa-4641
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00008.html
- https://security.gentoo.org/glsa/202006-08
- https://usn.ubuntu.com/4310-1/
- https://webkitgtk.org/security/WSA-2020-0003.html
- https://bugs.webkit.org/show_bug.cgi?id=204342#c21
