# [M] CVE-2017-18257

## Summary
Severity: Medium
Advisory: CVE-2017-18257
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-04
Source: https://osv.dev/vulnerability/CVE-2017-18257
Type: osv

## Details
The __get_data_block function in fs/f2fs/data.c in the Linux kernel before 4.11 allows local users to cause a denial of service (integer overflow and loop) via crafted use of the open and fallocate system calls with an FS_IOC_FIEMAP ioctl.

## References
- https://usn.ubuntu.com/3696-1/
- https://usn.ubuntu.com/3696-2/
- https://www.debian.org/security/2018/dsa-4188
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=b86e33075ed1909d8002745b56ecf73b833db143
- https://github.com/torvalds/linux/commit/b86e33075ed1909d8002745b56ecf73b833db143
