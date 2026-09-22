# [H] parisc: Fix non-access data TLB cache flush faults

## Summary
Severity: High
Advisory: CVE-2022-49172
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49172
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

parisc: Fix non-access data TLB cache flush faults

When a page is not present, we get non-access data TLB faults from
the fdc and fic instructions in flush_user_dcache_range_asm and
flush_user_icache_range_asm. When these occur, the cache line is
not invalidated and potentially we get memory corruption. The
problem was hidden by the nullification of the flush instructions.

These faults also affect performance. With pa8800/pa8900 processors,
there will be 32 faults per 4 KB page since the cache line is 128
bytes.  There will be more faults with earlier processors.

The problem is fixed by using flush_cache_pages(). It does the flush
using a tmp alias mapping.

The flush_cache_pages() call in flush_cache_range() flushed too
large a range.

V2: Remove unnecessary preempt_disable() and preempt_enable() calls.

## References
- https://git.kernel.org/stable/c/b3d6adb3a49d82e4e557c5fc16f50c9ff731da5d
- https://git.kernel.org/stable/c/ddca4b82027e2a66333dd40fab21a4beff435c7e
- https://git.kernel.org/stable/c/f839e5f1cef36ce268950c387129b1bfefdaebc9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49172.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49172
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
