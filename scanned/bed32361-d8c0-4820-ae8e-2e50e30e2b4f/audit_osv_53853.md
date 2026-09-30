# [M] CVE-2023-2898

## Summary
Severity: Medium
Advisory: CVE-2023-2898
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-26
Source: https://osv.dev/vulnerability/CVE-2023-2898
Type: osv

## Details
There is a null-pointer-dereference flaw found in f2fs_write_end_io in fs/f2fs/data.c in the Linux kernel. This flaw allows a local privileged user to cause a denial of service problem.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://security.netapp.com/advisory/ntap-20230929-0002/
- https://www.debian.org/security/2023/dsa-5480
- https://www.debian.org/security/2023/dsa-5492
- https://lore.kernel.org/linux-f2fs-devel/20230522124203.3838360-1-chao%40kernel.org/
