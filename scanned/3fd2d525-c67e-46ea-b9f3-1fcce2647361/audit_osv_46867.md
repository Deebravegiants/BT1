# [M] CVE-2015-7509

## Summary
Severity: Medium
Advisory: CVE-2015-7509
CVSS: 4.4 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2015-12-28
Source: https://osv.dev/vulnerability/CVE-2015-7509
Type: osv

## Details
fs/ext4/namei.c in the Linux kernel before 3.7 allows physically proximate attackers to cause a denial of service (system crash) via a crafted no-journal filesystem, a related issue to CVE-2013-2015.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c9b92530a723ac5ef8e352885a1862b18f31b2f5
- http://rhn.redhat.com/errata/RHSA-2016-0855.html
- https://github.com/torvalds/linux/commit/c9b92530a723ac5ef8e352885a1862b18f31b2f5
- https://bugzilla.redhat.com/show_bug.cgi?id=1259222
- https://bugzilla.suse.com/show_bug.cgi?id=956709
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00031.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00038.html
- http://www.securitytracker.com/id/1034559
- https://security-tracker.debian.org/tracker/CVE-2015-7509
