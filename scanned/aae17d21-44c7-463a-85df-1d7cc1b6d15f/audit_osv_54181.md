# [M] CVE-2023-4194

## Summary
Severity: Medium
Advisory: CVE-2023-4194
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-08-07
Source: https://osv.dev/vulnerability/CVE-2023-4194
Type: osv

## Details
A flaw was found in the Linux kernel's TUN/TAP functionality. This issue could allow a local user to bypass network filters and gain unauthorized access to some resources. The original patches fixing CVE-2023-1076 are incorrect or incomplete. The problem is that the following upstream commits - a096ccca6e50 ("tun: tun_chr_open(): correctly initialize socket uid"), - 66b2c338adce ("tap: tap_open(): correctly initialize socket uid"), pass "inode->i_uid" to sock_init_data_uid() as the last parameter and that turns out to not be accurate.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/344H6HO6SSC4KT7PDFXSDIXKMKHISSGF/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3TYLSJ2SAI7RF56ZLQ5CQWCJLVJSD73Q/
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://security.netapp.com/advisory/ntap-20231027-0002/
- https://access.redhat.com/security/cve/CVE-2023-4194
- https://www.debian.org/security/2023/dsa-5480
- https://www.debian.org/security/2023/dsa-5492
- https://access.redhat.com/errata/RHSA-2023:6583
- https://bugzilla.redhat.com/show_bug.cgi?id=2229498
- https://lore.kernel.org/all/20230731164237.48365-1-lersek@redhat.com/
- https://lore.kernel.org/all/20230731164237.48365-2-lersek@redhat.com/
- https://lore.kernel.org/all/20230731164237.48365-3-lersek@redhat.com/
