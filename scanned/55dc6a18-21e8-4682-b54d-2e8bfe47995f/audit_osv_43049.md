# [H] afs: Fix error code in afs_extract_vl_addrs()

## Summary
Severity: High
Advisory: CVE-2026-72378
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72378
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

afs: Fix error code in afs_extract_vl_addrs()

The error codes on these paths are only set on the first iteration
through the loop.  Set the correct error code on every iteration.

## References
- https://git.kernel.org/stable/c/4897cb71d4ab1f7e1a214adb1e4b80176702368d
- https://git.kernel.org/stable/c/4e0b047848a855f2c933a6439f76a01743ba5620
- https://git.kernel.org/stable/c/7ce6737a975ea3e0dc2e5946628d233779ca0caf
- https://git.kernel.org/stable/c/8530206911fd66ad739ca5ce95f1d069f3d42204
- https://git.kernel.org/stable/c/9ad9016e3333c3c1f9284a253ff0658369e07aac
- https://git.kernel.org/stable/c/bdcd80ff12939d172043fac5eb822b92366a1bab
- https://git.kernel.org/stable/c/cb33dd2968588c78fad78dec19f61cabe5785494
- https://git.kernel.org/stable/c/f70fbf2b974b63a7042705c2b0464cb8c97e9f34
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72378.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72378
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
