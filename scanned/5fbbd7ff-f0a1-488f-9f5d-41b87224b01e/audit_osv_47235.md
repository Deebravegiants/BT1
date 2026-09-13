# [H] CVE-2016-1575

## Summary
Severity: High
Advisory: CVE-2016-1575
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-02
Source: https://osv.dev/vulnerability/CVE-2016-1575
Type: osv

## Details
The overlayfs implementation in the Linux kernel through 4.5.2 does not properly maintain POSIX ACL xattr data, which allows local users to gain privileges by leveraging a group-writable setgid directory.

## References
- http://people.canonical.com/~ubuntu-security/cve/2016/CVE-2016-1575.html
- http://www.openwall.com/lists/oss-security/2016/02/24/7
- http://www.openwall.com/lists/oss-security/2021/10/18/1
- https://launchpad.net/bugs/1534961
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=e9f57ebcba563e0cd532926cab83c92bb4d79360
- http://www.halfdog.net/Security/2016/UserNamespaceOverlayfsXattrSetgidPrivilegeEscalation/
