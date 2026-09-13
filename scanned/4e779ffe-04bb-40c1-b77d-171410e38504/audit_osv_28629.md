# [H] mm: cachestat: fix two shmem bugs

## Summary
Severity: High
Advisory: CVE-2024-35797
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35797
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: cachestat: fix two shmem bugs

When cachestat on shmem races with swapping and invalidation, there
are two possible bugs:

1) A swapin error can have resulted in a poisoned swap entry in the
   shmem inode's xarray. Calling get_shadow_from_swap_cache() on it
   will result in an out-of-bounds access to swapper_spaces[].

   Validate the entry with non_swap_entry() before going further.

2) When we find a valid swap entry in the shmem's inode, the shadow
   entry in the swapcache might not exist yet: swap IO is still in
   progress and we're before __remove_mapping; swapin, invalidation,
   or swapoff have removed the shadow from swapcache after we saw the
   shmem swap entry.

   This will send a NULL to workingset_test_recent(). The latter
   purely operates on pointer bits, so it won't crash - node 0, memcg
   ID 0, eviction timestamp 0, etc. are all valid inputs - but it's a
   bogus test. In theory that could result in a false "recently
   evicted" count.

   Such a false positive wouldn't be the end of the world. But for
   code clarity and (future) robustness, be explicit about this case.

   Bail on get_shadow_from_swap_cache() returning NULL.

## References
- https://git.kernel.org/stable/c/24a0e73d544439bb9329fbbafac44299e548a677
- https://git.kernel.org/stable/c/b79f9e1ff27c994a4c452235ba09e672ec698e23
- https://git.kernel.org/stable/c/d5d39c707a4cf0bcc84680178677b97aa2cb2627
- https://git.kernel.org/stable/c/d962f6c583458037dc7e529659b2b02b9dd3d94b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35797.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35797
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
