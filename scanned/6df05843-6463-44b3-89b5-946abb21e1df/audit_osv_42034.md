# [C] smb: client: fix double-free in SMB2_ioctl() replay

## Summary
Severity: Critical
Advisory: CVE-2026-64385
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64385
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.145, >=6.7.0 <6.12.96, >=6.8.0 <6.18.39, >=6.13.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix double-free in SMB2_ioctl() replay

A response-bearing attempt can return a replayable error and free its
response buffer. If SMB2_ioctl_init() fails before the next send, cleanup
retains the previous buffer type and frees that response again.

Reset response bookkeeping before each attempt to prevent the stale free.

## References
- https://git.kernel.org/stable/c/0be4bc64882edaefaaee8d1e27d083643eb778e6
- https://git.kernel.org/stable/c/276c8efbc49f9303ac76d0d4deab7128581b0f3b
- https://git.kernel.org/stable/c/96fcfc8ae7359346156e492ca610e830d2649ad6
- https://git.kernel.org/stable/c/f9bbadb6c94583e3b4af1afc449bfceb1d1ddec9
- https://git.kernel.org/stable/c/fc65ffb4ef1bf540da16b17c225ae51091e07d72
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64385.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64385
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
