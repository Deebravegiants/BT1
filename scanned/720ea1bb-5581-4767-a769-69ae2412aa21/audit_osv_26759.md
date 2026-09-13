# [H] drm/amdkfd: fix potential kgd_mem UAFs

## Summary
Severity: High
Advisory: CVE-2023-53816
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2023-53816
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <6.1.23, >=6.2.0 <6.2.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: fix potential kgd_mem UAFs

kgd_mem pointers returned by kfd_process_device_translate_handle are
only guaranteed to be valid while p->mutex is held. As soon as the mutex
is unlocked, another thread can free the BO.

## References
- https://git.kernel.org/stable/c/5045360f3bb62ccd4f87202e33489f71f8bbc3fc
- https://git.kernel.org/stable/c/5ca14fb5552ac13a2402d306c0bd2379a71610ff
- https://git.kernel.org/stable/c/9da050b0d9e04439d225a2ec3044af70cdfb3933
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53816.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53816
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
