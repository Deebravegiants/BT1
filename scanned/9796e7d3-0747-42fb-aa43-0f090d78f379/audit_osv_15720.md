# [H] CVE-2019-19053

## Summary
Severity: High
Advisory: CVE-2019-19053
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19053
Type: osv

## Details
A memory leak in the rpmsg_eptdev_write_iter() function in drivers/rpmsg/rpmsg_char.c in the Linux kernel through 5.3.11 allows attackers to cause a denial of service (memory consumption) by triggering copy_from_iter_full() failures, aka CID-bbe692e349e2.

## References
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4300-1/
- https://usn.ubuntu.com/4301-1/
- https://github.com/torvalds/linux/commit/bbe692e349e2a1edf3fe0a29a0e05899c9c94d51
