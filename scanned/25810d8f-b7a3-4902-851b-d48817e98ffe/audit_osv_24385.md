# [H] Privilege escalation with IO_RING_OP_CLOSE in the Linux Kernel

## Summary
Severity: High
Advisory: CVE-2023-1295
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-28
Source: https://osv.dev/vulnerability/CVE-2023-1295
Type: osv

## Details
A time-of-check to time-of-use issue exists in io_uring subsystem's IORING_OP_CLOSE operation in the Linux kernel's versions 5.6 - 5.11 (inclusive), which allows a local user to elevate their privileges to root. Introduced in b5dba59e0cf7e2cc4d3b3b1ac5fe81ddf21959eb, patched in 9eac1904d3364254d622bf2c771c4f85cd435fc2, backported to stable in 788d0824269bef539fe31a785b1517882eafed93.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=b5dba59e0cf7e2cc4d3b3b1ac5fe81ddf21959eb
- https://kernel.dance/788d0824269bef539fe31a785b1517882eafed93
- https://kernel.dance/9eac1904d3364254d622bf2c771c4f85cd435fc2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1295.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1295
- https://security.netapp.com/advisory/ntap-20230731-0006/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=788d0824269bef539fe31a785b1517882eafed93
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=9eac1904d3364254d622bf2c771c4f85cd435fc2
