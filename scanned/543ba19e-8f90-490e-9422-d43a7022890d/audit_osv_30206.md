# [H] secretmem: disable memfd_secret() if arch cannot set direct map

## Summary
Severity: High
Advisory: CVE-2024-50182
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50182
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.169, >=5.16.0 <6.1.113, >=6.2.0 <6.6.57, >=6.7.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

secretmem: disable memfd_secret() if arch cannot set direct map

Return -ENOSYS from memfd_secret() syscall if !can_set_direct_map().  This
is the case for example on some arm64 configurations, where marking 4k
PTEs in the direct map not present can only be done if the direct map is
set up at 4k granularity in the first place (as ARM's break-before-make
semantics do not easily allow breaking apart large/gigantic pages).

More precisely, on arm64 systems with !can_set_direct_map(),
set_direct_map_invalid_noflush() is a no-op, however it returns success
(0) instead of an error.  This means that memfd_secret will seemingly
"work" (e.g.  syscall succeeds, you can mmap the fd and fault in pages),
but it does not actually achieve its goal of removing its memory from the
direct map.

Note that with this patch, memfd_secret() will start erroring on systems
where can_set_direct_map() returns false (arm64 with
CONFIG_RODATA_FULL_DEFAULT_ENABLED=n, CONFIG_DEBUG_PAGEALLOC=n and
CONFIG_KFENCE=n), but that still seems better than the current silent
failure.  Since CONFIG_RODATA_FULL_DEFAULT_ENABLED defaults to 'y', most
arm64 systems actually have a working memfd_secret() and aren't be
affected.

From going through the iterations of the original memfd_secret patch
series, it seems that disabling the syscall in these scenarios was the
intended behavior [1] (preferred over having
set_direct_map_invalid_noflush return an error as that would result in
SIGBUSes at page-fault time), however the check for it got dropped between
v16 [2] and v17 [3], when secretmem moved away from CMA allocations.

[1]: https://lore.kernel.org/lkml/20201124164930.GK8537@kernel.org/
[2]: https://lore.kernel.org/lkml/20210121122723.3446-11-rppt@kernel.org/#t
[3]: https://lore.kernel.org/lkml/20201125092208.12544-10-rppt@kernel.org/

## References
- https://git.kernel.org/stable/c/532b53cebe58f34ce1c0f34d866f5c0e335c53c6
- https://git.kernel.org/stable/c/5ea0b7af38754d2b45ead9257bca47e84662e926
- https://git.kernel.org/stable/c/757786abe4547eb3d9d0e8350a63bdb0f9824af2
- https://git.kernel.org/stable/c/7caf966390e6e4ebf42775df54e7ee1f280ce677
- https://git.kernel.org/stable/c/d0ae6ffa1aeb297aef89f49cfb894a83c329ebad
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50182.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50182
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
