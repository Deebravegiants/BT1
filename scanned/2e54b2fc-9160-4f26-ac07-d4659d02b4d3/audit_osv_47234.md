# [H] CVE-2016-1572

## Summary
Severity: High
Advisory: CVE-2016-1572
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-01-22
Source: https://osv.dev/vulnerability/CVE-2016-1572
Type: osv

## Details
mount.ecryptfs_private.c in eCryptfs-utils does not validate mount destination filesystem types, which allows local users to gain privileges by mounting over a nonstandard filesystem, as demonstrated by /proc/$pid.

## References
- http://lists.opensuse.org/opensuse-updates/2016-01/msg00091.html
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00004.html
- http://www.openwall.com/lists/oss-security/2016/01/20/6
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/177359.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/177396.html
- http://lists.opensuse.org/opensuse-updates/2016-01/msg00118.html
- http://www.securitytracker.com/id/1034791
- https://bugs.launchpad.net/ecryptfs/+bug/1530566
- http://www.debian.org/security/2016/dsa-3450
- http://www.ubuntu.com/usn/USN-2876-1
- https://bazaar.launchpad.net/~ecryptfs/ecryptfs/trunk/revision/870
