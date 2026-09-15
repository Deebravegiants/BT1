# [H] crypto: ccp - Check for page allocation failure correctly in TIO

## Summary
Severity: High
Advisory: CVE-2026-74403
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74403
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: ccp - Check for page allocation failure correctly in TIO

Sashiko notes:

> if __snp_alloc_firmware_pages() returns NULL under memory pressure, is it
> safe to pass it directly to page_address()?
>
> On architectures without HASHED_PAGE_VIRTUAL, page_address(NULL) might
> compute a deterministic but invalid, non-zero virtual address. The
> subsequent if (tio_status) check would then evaluate to true, and
> sev_tsm_init_locked() would dereference the invalid pointer.

Indeed, page_address(NULL) will return non-NULL garbage here. Fix this by
checking the page allocation itself for NULL, not the resulting virtual
address.

## References
- https://git.kernel.org/stable/c/17e1aae19a06d9f6da4b46d54fa2aeab77ec0c69
- https://git.kernel.org/stable/c/a8d5370eef00eca132a292b1901c9914c817e385
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74403.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74403
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
