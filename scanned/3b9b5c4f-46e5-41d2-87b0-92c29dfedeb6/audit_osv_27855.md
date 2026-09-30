# [H] mm: cachestat: fix folio read-after-free in cache walk

## Summary
Severity: High
Advisory: CVE-2024-26630
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-03-13
Source: https://osv.dev/vulnerability/CVE-2024-26630
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.21, >=6.7.0 <6.7.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: cachestat: fix folio read-after-free in cache walk

In cachestat, we access the folio from the page cache's xarray to compute
its page offset, and check for its dirty and writeback flags.  However, we
do not hold a reference to the folio before performing these actions,
which means the folio can concurrently be released and reused as another
folio/page/slab.

Get around this altogether by just using xarray's existing machinery for
the folio page offsets and dirty/writeback states.

This changes behavior for tmpfs files to now always report zeroes in their
dirty and writeback counters.  This is okay as tmpfs doesn't follow
conventional writeback cache behavior: its pages get "cleaned" during
swapout, after which they're no longer resident etc.

## References
- https://git.kernel.org/stable/c/3a75cb05d53f4a6823a32deb078de1366954a804
- https://git.kernel.org/stable/c/ba60fdf75e89ea762bb617be578dc47f27655117
- https://git.kernel.org/stable/c/fe7e008e0ce728252e4ec652cceebcc62211657c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26630.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26630
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
