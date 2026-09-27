# [M] scsi: qedf: Ensure the copied buf is NUL terminated

## Summary
Severity: Medium
Advisory: CVE-2024-38559
Ecosystem: Linux
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38559
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <4.19.316, >=4.20.0 <5.4.278, >=5.5.0 <5.10.219, >=5.11.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qedf: Ensure the copied buf is NUL terminated

Currently, we allocate a count-sized kernel buffer and copy count from
userspace to that buffer. Later, we use kstrtouint on this buffer but we
don't ensure that the string is terminated inside the buffer, this can
lead to OOB read when using kstrtouint. Fix this issue by using
memdup_user_nul instead of memdup_user.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/177f43c6892e6055de6541fe9391a8a3d1f95fc9
- https://git.kernel.org/stable/c/1f84a2744ad813be23fc4be99fb74bfb24aadb95
- https://git.kernel.org/stable/c/4907f5ad246fa9b51093ed7dfc7da9ebbd3f20b8
- https://git.kernel.org/stable/c/563e609275927c0b75fbfd0d90441543aa7b5e0d
- https://git.kernel.org/stable/c/769b9fd2af02c069451fe9108dba73355d9a021c
- https://git.kernel.org/stable/c/a75001678e1d38aa607d5b898ec7ff8ed0700d59
- https://git.kernel.org/stable/c/d0184a375ee797eb657d74861ba0935b6e405c62
- https://git.kernel.org/stable/c/d93318f19d1e1a6d5f04f5d965eaa9055bb7c613
- https://git.kernel.org/stable/c/dccd97b39ab2f2b1b9a47a1394647a4d65815255
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38559.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38559
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
