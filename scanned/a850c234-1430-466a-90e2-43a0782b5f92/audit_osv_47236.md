# [H] CVE-2016-1576

## Summary
Severity: High
Advisory: CVE-2016-1576
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-02
Source: https://osv.dev/vulnerability/CVE-2016-1576
Type: osv

## Details
The overlayfs implementation in the Linux kernel through 4.5.2 does not properly restrict the mount namespace, which allows local users to gain privileges by mounting an overlayfs filesystem on top of a FUSE filesystem, and then executing a crafted setuid program.

## References
- http://people.canonical.com/~ubuntu-security/cve/2016/CVE-2016-1576.html
- http://www.openwall.com/lists/oss-security/2016/02/24/8
- http://www.openwall.com/lists/oss-security/2021/10/18/1
- https://bugs.launchpad.net/bugs/1535150
- https://launchpadlibrarian.net/235300093/0005-overlayfs-Be-more-careful-about-copying-up-sxid-file.patch
- https://launchpadlibrarian.net/235300225/0006-overlayfs-Propogate-nosuid-from-lower-and-upper-moun.patch
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=e9f57ebcba563e0cd532926cab83c92bb4d79360
- http://www.halfdog.net/Security/2016/OverlayfsOverFusePrivilegeEscalation/
