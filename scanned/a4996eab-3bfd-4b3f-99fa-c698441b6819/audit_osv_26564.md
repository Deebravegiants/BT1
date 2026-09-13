# [M] accel/qaic: Fix slicing memory leak

## Summary
Severity: Medium
Advisory: CVE-2023-53350
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2023-53350
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.4.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/qaic: Fix slicing memory leak

The temporary buffer storing slicing configuration data from user is only
freed on error.  This is a memory leak.  Free the buffer unconditionally.

## References
- https://git.kernel.org/stable/c/2d956177b7c96e62fac762a3b7da4318cde27a73
- https://git.kernel.org/stable/c/df45c3e46cdb41f486eecb4277fbcc4c1ffbf9be
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53350.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53350
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
