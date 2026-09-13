# [M] CVE-2016-6198

## Summary
Severity: Medium
Advisory: CVE-2016-6198
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2016-6198
Type: osv

## Details
The filesystem layer in the Linux kernel before 4.5.5 proceeds with post-rename operations after an OverlayFS file is renamed to a self-hardlink, which allows local users to cause a denial of service (system crash) via a rename system call, related to fs/namei.c and fs/open.c.

## References
- http://www.securityfocus.com/bid/91709
- http://www.securitytracker.com/id/1036273
- http://rhn.redhat.com/errata/RHSA-2016-1875.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.5.5
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://rhn.redhat.com/errata/RHSA-2016-2584.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://rhn.redhat.com/errata/RHSA-2016-1847.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1355654
- https://github.com/torvalds/linux/commit/54d5ca871e72f2bb172ec9323497f01cd5091ec7
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=54d5ca871e72f2bb172ec9323497f01cd5091ec7
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=9409e22acdfc9153f88d9b1ed2bd2a5b34d2d3ca
- https://github.com/torvalds/linux/commit/9409e22acdfc9153f88d9b1ed2bd2a5b34d2d3ca
- http://www.openwall.com/lists/oss-security/2016/07/11/8
