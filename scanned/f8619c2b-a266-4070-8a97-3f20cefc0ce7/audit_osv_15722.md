# [H] CVE-2019-19060

## Summary
Severity: High
Advisory: CVE-2019-19060
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19060
Type: osv

## Details
A memory leak in the adis_update_scan_mode() function in drivers/iio/imu/adis_buffer.c in the Linux kernel before 5.3.9 allows attackers to cause a denial of service (memory consumption), aka CID-ab612b1daf41.

## References
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4208-1/
- https://usn.ubuntu.com/4210-1/
- https://usn.ubuntu.com/4226-1/
- https://usn.ubuntu.com/4364-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.9
- https://github.com/torvalds/linux/commit/ab612b1daf415b62c58e130cb3d0f30b255a14d0
