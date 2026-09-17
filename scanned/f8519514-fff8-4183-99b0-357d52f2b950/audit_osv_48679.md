# [M] CVE-2018-1095

## Summary
Severity: Medium
Advisory: CVE-2018-1095
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-02
Source: https://osv.dev/vulnerability/CVE-2018-1095
Type: osv

## Details
The ext4_xattr_check_entries function in fs/ext4/xattr.c in the Linux kernel through 4.15.15 does not properly validate xattr sizes, which causes misinterpretation of a size as an error code, and consequently allows attackers to cause a denial of service (get_acl NULL pointer dereference and system crash) via a crafted ext4 image.

## References
- https://usn.ubuntu.com/3695-2/
- https://usn.ubuntu.com/3695-1/
- https://access.redhat.com/errata/RHSA-2018:2948
- https://bugzilla.kernel.org/show_bug.cgi?id=199185
- https://bugzilla.redhat.com/show_bug.cgi?id=1560793
- https://git.kernel.org/pub/scm/linux/kernel/git/tytso/ext4.git/commit/?id=ce3fd194fcc6fbdc00ce095a852f22df97baa401
- http://openwall.com/lists/oss-security/2018/03/29/1
