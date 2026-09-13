# [M] CVE-2019-19815

## Summary
Severity: Medium
Advisory: CVE-2019-19815
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-12-17
Source: https://osv.dev/vulnerability/CVE-2019-19815
Type: osv

## Details
In the Linux kernel 5.0.21, mounting a crafted f2fs filesystem image can cause a NULL pointer dereference in f2fs_recover_fsync_data in fs/f2fs/recovery.c. This is related to F2FS_P_SB in fs/f2fs/f2fs.h.

## References
- https://security.netapp.com/advisory/ntap-20200103-0001/
- https://github.com/torvalds/linux/commit/4969c06a0d83c9c3dc50b8efcdc8eeedfce896f6#diff-41a7fa4590d2af87e82101f2b4dadb56
- https://github.com/bobfuzzer/CVE/tree/master/CVE-2019-19815
