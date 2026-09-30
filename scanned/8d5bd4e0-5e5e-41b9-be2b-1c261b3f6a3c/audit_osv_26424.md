# [H] mm: fix zswap writeback race condition

## Summary
Severity: High
Advisory: CVE-2023-53178
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53178
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.11.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: fix zswap writeback race condition

The zswap writeback mechanism can cause a race condition resulting in
memory corruption, where a swapped out page gets swapped in with data that
was written to a different page.

The race unfolds like this:
1. a page with data A and swap offset X is stored in zswap
2. page A is removed off the LRU by zpool driver for writeback in
   zswap-shrink work, data for A is mapped by zpool driver
3. user space program faults and invalidates page entry A, offset X is
   considered free
4. kswapd stores page B at offset X in zswap (zswap could also be
   full, if so, page B would then be IOed to X, then skip step 5.)
5. entry A is replaced by B in tree->rbroot, this doesn't affect the
   local reference held by zswap-shrink work
6. zswap-shrink work writes back A at X, and frees zswap entry A
7. swapin of slot X brings A in memory instead of B

The fix:
Once the swap page cache has been allocated (case ZSWAP_SWAPCACHE_NEW),
zswap-shrink work just checks that the local zswap_entry reference is
still the same as the one in the tree.  If it's not the same it means that
it's either been invalidated or replaced, in both cases the writeback is
aborted because the local entry contains stale data.

Reproducer:
I originally found this by running `stress` overnight to validate my work
on the zswap writeback mechanism, it manifested after hours on my test
machine.  The key to make it happen is having zswap writebacks, so
whatever setup pumps /sys/kernel/debug/zswap/written_back_pages should do
the trick.

In order to reproduce this faster on a vm, I setup a system with ~100M of
available memory and a 500M swap file, then running `stress --vm 1
--vm-bytes 300000000 --vm-stride 4000` makes it happen in matter of tens
of minutes.  One can speed things up even more by swinging
/sys/module/zswap/parameters/max_pool_percent up and down between, say, 20
and 1; this makes it reproduce in tens of seconds.  It's crucial to set
`--vm-stride` to something other than 4096 otherwise `stress` won't
realize that memory has been corrupted because all pages would have the
same data.

## References
- https://git.kernel.org/stable/c/04fc7816089c5a32c29a04ec94b998e219dfb946
- https://git.kernel.org/stable/c/2cab13f500a6333bd2b853783ac76be9e4956f8a
- https://git.kernel.org/stable/c/ba700ea13bf0105a4773c654f7d3bef8adb64ab2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53178.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53178
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
