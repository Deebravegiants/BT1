# [H] xfs: add bounds checking to xlog_recover_process_data

## Summary
Severity: High
Advisory: CVE-2024-41014
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41014
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.1.120, >=6.2.0 <6.6.64

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfs: add bounds checking to xlog_recover_process_data

There is a lack of verification of the space occupied by fixed members
of xlog_op_header in the xlog_recover_process_data.

We can create a crafted image to trigger an out of bounds read by
following these steps:
    1) Mount an image of xfs, and do some file operations to leave records
    2) Before umounting, copy the image for subsequent steps to simulate
       abnormal exit. Because umount will ensure that tail_blk and
       head_blk are the same, which will result in the inability to enter
       xlog_recover_process_data
    3) Write a tool to parse and modify the copied image in step 2
    4) Make the end of the xlog_op_header entries only 1 byte away from
       xlog_rec_header->h_size
    5) xlog_rec_header->h_num_logops++
    6) Modify xlog_rec_header->h_crc

Fix:
Add a check to make sure there is sufficient space to access fixed members
of xlog_op_header.

## References
- https://git.kernel.org/stable/c/7cd9f0a33e738cd58876f1bc8d6c1aa5bc4fc8c1
- https://git.kernel.org/stable/c/d1e3efe783365db59da88f08a2e0bfe1cc95b143
- https://git.kernel.org/stable/c/fb63435b7c7dc112b1ae1baea5486e0a6e27b196
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41014.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41014
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
