# [H] lockd: set other missing fields when unlocking files

## Summary
Severity: High
Advisory: CVE-2022-50302
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2022-50302
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.86, >=5.16.0 <6.0.16, >=5.19.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

lockd: set other missing fields when unlocking files

vfs_lock_file() expects the struct file_lock to be fully initialised by
the caller. Re-exported NFSv3 has been seen to Oops if the fl_file field
is NULL.

## References
- https://git.kernel.org/stable/c/18ebd35b61b4693a0ddc270b6d4f18def232e770
- https://git.kernel.org/stable/c/31c93ee5f1e4dc278b562e20f3c3274ac34997f3
- https://git.kernel.org/stable/c/688575aef211b0986fc51010116f5888a99d76a2
- https://git.kernel.org/stable/c/95d42a8d3d4ae84a0bd3ee23e1fee240cdf0a9f0
- https://git.kernel.org/stable/c/d7aa9f7778316beb690f6e2763b6d672ad8b256f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50302.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50302
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
