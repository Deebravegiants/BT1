# [H] crypto: ccp - Fix snp_filter_reserved_mem_regions() off-by-one

## Summary
Severity: High
Advisory: CVE-2026-74404
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74404
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: ccp - Fix snp_filter_reserved_mem_regions() off-by-one

Sashiko notes:

> regarding the bounds check in snp_filter_reserved_mem_regions()
> called via walk_iomem_res_desc(): does the check
> if ((range_list->num_elements * 16 + 8) > PAGE_SIZE)
> allow an off-by-one heap buffer overflow?
>
> If range_list->num_elements is 255, 255 * 16 + 8 = 4088, which is <= 4096.
> Writing range->base (8 bytes) fills 4088-4095, but writing range->page_count
> (4 bytes) would write to 4096-4099, overflowing the kzalloc-allocated
> PAGE_SIZE buffer.

Fix this by accounting for the entry about to be written to, in addition to
the entries that are already allocated.

## References
- https://git.kernel.org/stable/c/1b864b6cb213bbd7b406e9b2e98c962077f300df
- https://git.kernel.org/stable/c/830c1f3e71989448652973375ef5e39b6ede47a3
- https://git.kernel.org/stable/c/af7341616b742ad2c374a90998bd650a035f694d
- https://git.kernel.org/stable/c/c5c79d92da0f9a09f48be5e2aabed2d6d1a96294
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74404.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74404
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
