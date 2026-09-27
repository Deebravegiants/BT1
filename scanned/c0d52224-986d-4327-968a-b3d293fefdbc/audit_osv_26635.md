# [M] cassini: Fix a memory leak in the error handling path of cas_init_one()

## Summary
Severity: Medium
Advisory: CVE-2023-53435
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53435
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.28 <4.14.316, >=4.15.0 <4.19.284, >=4.20.0 <5.4.244, >=5.5.0 <5.10.181, >=5.11.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

cassini: Fix a memory leak in the error handling path of cas_init_one()

cas_saturn_firmware_init() allocates some memory using vmalloc(). This
memory is freed in the .remove() function but not it the error handling
path of the probe.

Add the missing vfree() to avoid a memory leak, should an error occur.

## References
- https://git.kernel.org/stable/c/11c0ed097a874156957b515d0ba7e356142eab87
- https://git.kernel.org/stable/c/172146c26f0c1b86ab4e9ebffc7e06f04229fa17
- https://git.kernel.org/stable/c/234e744d86bd95b381d24546df2dba72804e0219
- https://git.kernel.org/stable/c/412cd77a2c24b191c65ea53025222418db09817c
- https://git.kernel.org/stable/c/60d8e8b88087d68e10c8991a0f6733fa2f963ff0
- https://git.kernel.org/stable/c/b8b1a667744741fa7807b09a12797a27f14f3fac
- https://git.kernel.org/stable/c/dc61f7582cc92d547d02e141cd66f5d1f4ed8012
- https://git.kernel.org/stable/c/e20105d967ab5b53ff50a0e5991fe37324d2ba20
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53435.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53435
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
