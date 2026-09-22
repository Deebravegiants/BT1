# [H] net: lan966x: fix use-after-free and leak in lan966x_fdma_reload()

## Summary
Severity: High
Advisory: CVE-2026-31644
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31644
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.82, >=6.13.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: lan966x: fix use-after-free and leak in lan966x_fdma_reload()

When lan966x_fdma_reload() fails to allocate new RX buffers, the restore
path restarts DMA using old descriptors whose pages were already freed
via lan966x_fdma_rx_free_pages(). Since page_pool_put_full_page() can
release pages back to the buddy allocator, the hardware may DMA into
memory now owned by other kernel subsystems.

Additionally, on the restore path, the newly created page pool (if
allocation partially succeeded) is overwritten without being destroyed,
leaking it.

Fix both issues by deferring the release of old pages until after the
new allocation succeeds. Save the old page array before the allocation
so old pages can be freed on the success path. On the failure path, the
old descriptors, pages and page pool are all still valid, making the
restore safe. Also ensure the restore path re-enables NAPI and wakes
the netdev, matching the success path.

## References
- https://git.kernel.org/stable/c/59c3d55a946cacdb4181600723c20ac4f4c20c84
- https://git.kernel.org/stable/c/691082c0b93c13a5e068c0905f673060bddc204e
- https://git.kernel.org/stable/c/92a673019943770930e2a8bfd52e1aad47a1fc1f
- https://git.kernel.org/stable/c/9950e9199b3dfdfbde0b8d96ba947d7b11243801
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31644.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31644
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
