# [H] platform/x86/amd: pmf: Use device managed allocations

## Summary
Severity: High
Advisory: CVE-2025-38421
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38421
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

platform/x86/amd: pmf: Use device managed allocations

If setting up smart PC fails for any reason then this can lead to
a double free when unloading amd-pmf.  This is because dev->buf was
freed but never set to NULL and is again freed in amd_pmf_remove().

To avoid subtle allocation bugs in failures leading to a double free
change all allocations into device managed allocations.

## References
- https://git.kernel.org/stable/c/0d10b532f861253c283863522d59d099fcb0796d
- https://git.kernel.org/stable/c/d9db3a941270d92bbd1a6a6b54a10324484f2f2d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38421.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38421
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
