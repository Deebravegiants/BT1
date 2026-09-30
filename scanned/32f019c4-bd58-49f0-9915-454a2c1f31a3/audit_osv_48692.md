# [M] CVE-2018-11412

## Summary
Severity: Medium
Advisory: CVE-2018-11412
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-24
Source: https://osv.dev/vulnerability/CVE-2018-11412
Type: osv

## Details
In the Linux kernel 4.13 through 4.16.11, ext4_read_inline_data() in fs/ext4/inline.c performs a memcpy with an untrusted length value in certain circumstances involving a crafted filesystem that stores the system.data extended attribute value in a dedicated inode.

## References
- http://www.securityfocus.com/bid/104291
- https://access.redhat.com/errata/RHSA-2019:0525
- https://usn.ubuntu.com/3752-1/
- https://usn.ubuntu.com/3752-2/
- https://usn.ubuntu.com/3752-3/
- https://bugzilla.kernel.org/show_bug.cgi?id=199803
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1580
- https://www.exploit-db.com/exploits/44832/
