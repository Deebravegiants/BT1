# [M] CVE-2019-18811

## Summary
Severity: Medium
Advisory: CVE-2019-18811
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-07
Source: https://osv.dev/vulnerability/CVE-2019-18811
Type: osv

## Details
A memory leak in the sof_set_get_large_ctrl_data() function in sound/soc/sof/ipc.c in the Linux kernel through 5.3.9 allows attackers to cause a denial of service (memory consumption) by triggering sof_get_ctrl_copy_params() failures, aka CID-45c1380358b1.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LYIFGYEDQXP5DVJQQUARQRK2PXKBKQGY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YWWOOJKZ4NQYN4RMFIVJ3ZIXKJJI3MKP/
- https://usn.ubuntu.com/4284-1/
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://github.com/torvalds/linux/commit/45c1380358b12bf2d1db20a5874e9544f56b34ab
