# [M] drm/lima: fix a memleak in lima_heap_alloc

## Summary
Severity: Medium
Advisory: CVE-2024-35829
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35829
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/lima: fix a memleak in lima_heap_alloc

When lima_vm_map_bo fails, the resources need to be deallocated, or
there will be memleaks.

## References
- https://git.kernel.org/stable/c/04ae3eb470e52a3c41babe85ff8cee195e4dcbea
- https://git.kernel.org/stable/c/4ab14eccf5578af1dd5668a5f2d771df27683cab
- https://git.kernel.org/stable/c/746606d37d662c70ae1379fc658ee9c65f06880f
- https://git.kernel.org/stable/c/8e25c0ee5665e8a768b8e21445db1f86e9156eb7
- https://git.kernel.org/stable/c/ec6bb037e4a35fcbb5cd7bc78242d034ed893fcd
- https://git.kernel.org/stable/c/f2e80ac9344aebbff576453d5c0290b332e187ed
- https://git.kernel.org/stable/c/f6d51a91b41704704e395de6839c667b0f810bbf
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35829.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35829
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
