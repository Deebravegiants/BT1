# [H] riscv: mm: Fix the out of bound issue of vmemmap address

## Summary
Severity: High
Advisory: CVE-2024-57945
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2024-57945
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.258, >=5.11.0 <6.1.140, >=6.2.0 <6.6.72, >=6.7.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

riscv: mm: Fix the out of bound issue of vmemmap address

In sparse vmemmap model, the virtual address of vmemmap is calculated as:
((struct page *)VMEMMAP_START - (phys_ram_base >> PAGE_SHIFT)).
And the struct page's va can be calculated with an offset:
(vmemmap + (pfn)).

However, when initializing struct pages, kernel actually starts from the
first page from the same section that phys_ram_base belongs to. If the
first page's physical address is not (phys_ram_base >> PAGE_SHIFT), then
we get an va below VMEMMAP_START when calculating va for it's struct page.

For example, if phys_ram_base starts from 0x82000000 with pfn 0x82000, the
first page in the same section is actually pfn 0x80000. During
init_unavailable_range(), we will initialize struct page for pfn 0x80000
with virtual address ((struct page *)VMEMMAP_START - 0x2000), which is
below VMEMMAP_START as well as PCI_IO_END.

This commit fixes this bug by introducing a new variable
'vmemmap_start_pfn' which is aligned with memory section size and using
it to calculate vmemmap address instead of phys_ram_base.

## References
- https://git.kernel.org/stable/c/04350304428063da6a55a8a4597d409dc69148b2
- https://git.kernel.org/stable/c/92f08673d3f1893191323572f60e3c62f2e57c2f
- https://git.kernel.org/stable/c/a4a7ac3d266008018f05fae53060fcb331151a14
- https://git.kernel.org/stable/c/d2bd51954ac8377c2f1eb1813e694788998add66
- https://git.kernel.org/stable/c/f754f27e98f88428aaf6be6e00f5cbce97f62d4b
- https://lists.debian.org/debian-lts-announce/2025/08/msg00010.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57945.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57945
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
