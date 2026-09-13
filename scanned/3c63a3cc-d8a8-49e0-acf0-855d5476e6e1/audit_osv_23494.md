# [H] drm/shmem-helper: Remove errant put in error path

## Summary
Severity: High
Advisory: CVE-2022-48981
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2022-48981
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.4.227, >=5.5.0 <5.10.159, >=5.11.0 <5.15.83, >=5.16.0 <6.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/shmem-helper: Remove errant put in error path

drm_gem_shmem_mmap() doesn't own this reference, resulting in the GEM
object getting prematurely freed leading to a later use-after-free.

## References
- https://git.kernel.org/stable/c/24013314be6ee4ee456114a671e9fa3461323de8
- https://git.kernel.org/stable/c/585a07b820059462e0c93b76c7de2cd946b26b40
- https://git.kernel.org/stable/c/586847b98e20ab02212ca5c1fc46680384e68a28
- https://git.kernel.org/stable/c/6a4da05acd062ae7774b6b19cef2b7d922902d36
- https://git.kernel.org/stable/c/83e3da8bb92fcfa7a1d232cf55f9e6c49bb84942
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48981.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48981
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
