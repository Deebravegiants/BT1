# [M] CVE-2018-1092

## Summary
Severity: Medium
Advisory: CVE-2018-1092
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-02
Source: https://osv.dev/vulnerability/CVE-2018-1092
Type: osv

## Details
The ext4_iget function in fs/ext4/inode.c in the Linux kernel through 4.15.15 mishandles the case of a root directory with a zero i_links_count, which allows attackers to cause a denial of service (ext4_process_freed_data NULL pointer dereference and OOPS) via a crafted ext4 image.

## References
- https://lists.debian.org/debian-lts-announce/2018/05/msg00000.html
- https://usn.ubuntu.com/3676-2/
- https://usn.ubuntu.com/3677-2/
- https://usn.ubuntu.com/3678-1/
- https://usn.ubuntu.com/3678-4/
- https://usn.ubuntu.com/3678-3/
- https://usn.ubuntu.com/3676-1/
- https://usn.ubuntu.com/3677-1/
- https://usn.ubuntu.com/3678-2/
- https://usn.ubuntu.com/3754-1/
- http://openwall.com/lists/oss-security/2018/03/29/1
- https://access.redhat.com/errata/RHSA-2018:2948
- https://www.debian.org/security/2018/dsa-4187
- https://access.redhat.com/errata/RHSA-2018:3096
- https://access.redhat.com/errata/RHSA-2018:3083
- https://www.debian.org/security/2018/dsa-4188
- https://bugzilla.kernel.org/show_bug.cgi?id=199179
- https://bugzilla.kernel.org/show_bug.cgi?id=199275
- https://bugzilla.redhat.com/show_bug.cgi?id=1560777
- https://git.kernel.org/pub/scm/linux/kernel/git/tytso/ext4.git/commit/?id=8e4b5eae5decd9dfe5a4ee369c22028f90ab4c44
