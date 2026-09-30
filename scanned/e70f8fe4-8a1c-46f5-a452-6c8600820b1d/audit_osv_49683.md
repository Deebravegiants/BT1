# [M] CVE-2019-15920

## Summary
Severity: Medium
Advisory: CVE-2019-15920
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-09-04
Source: https://osv.dev/vulnerability/CVE-2019-15920
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.0.10. SMB2_read in fs/cifs/smb2pdu.c has a use-after-free. NOTE: this was not fixed correctly in 5.0.10; see the 5.0.11 ChangeLog, which documents a memory leak.

## References
- https://security.netapp.com/advisory/ntap-20191004-0001/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.10
- https://github.com/torvalds/linux/commit/088aaf17aa79300cab14dbee2569c58cfafd7d6e
