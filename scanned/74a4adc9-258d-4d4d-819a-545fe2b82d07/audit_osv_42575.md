# [C] ksmbd: use opener credentials for FSCTL mutations

## Summary
Severity: Critical
Advisory: CVE-2026-68457
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-68457
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: use opener credentials for FSCTL mutations

SET_SPARSE, SET_ZERO_DATA and SET_COMPRESSION operate on an open SMB
handle but call VFS xattr, fallocate or fileattr helpers with the current
ksmbd worker credentials. Those helpers can revalidate inode permissions,
ownership and LSM policy independently of the SMB handle access mask.

Run each operation with the credentials captured in the target file when
the handle was opened. Keep credential handling local to these single-file
FSCTLs rather than applying session credentials to the complete IOCTL
handler, which also contains handle-less and multi-handle operations.

## References
- https://git.kernel.org/stable/c/1e112c47ec5dd1942e2d4ca6e8e9b712238e20c2
- https://git.kernel.org/stable/c/a8c18434e1f0d9f7989170bdb0490c0160baf065
- https://git.kernel.org/stable/c/c6394bcaf254c5baf9aff43376020be5db6d3316
- https://git.kernel.org/stable/c/cfb2c6f71d61ed807c9d7a7af331d406f1f31877
- https://git.kernel.org/stable/c/e205f3e7e8c31a47cd11efb6cf663a527177e432
- https://git.kernel.org/stable/c/fb1cae6302d58414ddf029e3f642711bd30243f7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68457.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68457
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
