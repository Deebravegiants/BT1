# [M] CVE-2020-14308

## Summary
Severity: Medium
Advisory: CVE-2020-14308
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-29
Source: https://osv.dev/vulnerability/CVE-2020-14308
Type: osv

## Details
In grub2 versions before 2.06 the grub memory allocator doesn't check for possible arithmetic overflows on the requested allocation size. This leads the function to return invalid memory allocations which can be further used to cause possible integrity, confidentiality and availability impacts during the boot process.

## References
- http://www.openwall.com/lists/oss-security/2021/09/17/4
- http://www.openwall.com/lists/oss-security/2021/09/21/1
- https://security.netapp.com/advisory/ntap-20200731-0008/
- https://usn.ubuntu.com/4432-1/
- http://www.openwall.com/lists/oss-security/2021/09/17/2
- https://security.gentoo.org/glsa/202104-05
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00017.html
- http://www.openwall.com/lists/oss-security/2020/07/29/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1852009
