# [M] CVE-2020-8992

## Summary
Severity: Medium
Advisory: CVE-2020-8992
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-14
Source: https://osv.dev/vulnerability/CVE-2020-8992
Type: osv

## Details
ext4_protect_reserved_inode in fs/ext4/block_validity.c in the Linux kernel through 5.5.3 allows attackers to cause a denial of service (soft lockup) via a crafted journal size.

## References
- https://usn.ubuntu.com/4324-1/
- https://usn.ubuntu.com/4342-1/
- https://usn.ubuntu.com/4344-1/
- https://usn.ubuntu.com/4419-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://security.netapp.com/advisory/ntap-20200313-0003/
- https://usn.ubuntu.com/4318-1/
- https://patchwork.ozlabs.org/patch/1236118/
