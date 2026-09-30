# [H] CVE-2019-19061

## Summary
Severity: High
Advisory: CVE-2019-19061
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19061
Type: osv

## Details
A memory leak in the adis_update_scan_mode_burst() function in drivers/iio/imu/adis_buffer.c in the Linux kernel before 5.3.9 allows attackers to cause a denial of service (memory consumption), aka CID-9c0530e898f3.

## References
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4208-1/
- https://usn.ubuntu.com/4526-1/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.9
- https://github.com/torvalds/linux/commit/9c0530e898f384c5d279bfcebd8bb17af1105873
