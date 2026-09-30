# [M] CVE-2018-10883

## Summary
Severity: Medium
Advisory: CVE-2018-10883
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-30
Source: https://osv.dev/vulnerability/CVE-2018-10883
Type: osv

## Details
A flaw was found in the Linux kernel's ext4 filesystem. A local user can cause an out-of-bounds write in jbd2_journal_dirty_metadata(), a denial of service, and a system crash by mounting and operating on a crafted ext4 filesystem image.

## References
- https://support.f5.com/csp/article/K94735334?utm_source=f5support&amp%3Butm_medium=RSS
- https://usn.ubuntu.com/3871-1/
- https://usn.ubuntu.com/3871-3/
- https://usn.ubuntu.com/3871-4/
- https://usn.ubuntu.com/3879-1/
- https://access.redhat.com/errata/RHSA-2018:3096
- https://lists.debian.org/debian-lts-announce/2018/07/msg00020.html
- https://usn.ubuntu.com/3871-5/
- https://usn.ubuntu.com/3879-2/
- https://access.redhat.com/errata/RHSA-2018:2948
- https://access.redhat.com/errata/RHSA-2018:3083
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10883
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=8bc1379b82b8e809eef77a9fedbb75c6c297be19
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=e09463f220ca9a1a1ecfda84fcda658f99a1f12a
