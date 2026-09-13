# [H] efi: stmm: Fix incorrect buffer allocation method

## Summary
Severity: High
Advisory: CVE-2025-39836
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-39836
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.45, >=6.13.0 <6.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

efi: stmm: Fix incorrect buffer allocation method

The communication buffer allocated by setup_mm_hdr() is later on passed
to tee_shm_register_kernel_buf(). The latter expects those buffers to be
contiguous pages, but setup_mm_hdr() just uses kmalloc(). That can cause
various corruptions or BUGs, specifically since commit 9aec2fb0fd5e
("slab: allocate frozen pages"), though it was broken before as well.

Fix this by using alloc_pages_exact() instead of kmalloc().

## References
- https://git.kernel.org/stable/c/630c0e6064daf84f17aad1a7d9ca76b562e3fe47
- https://git.kernel.org/stable/c/77ff27ff0e4529a003c8a1c2492c111968c378d3
- https://git.kernel.org/stable/c/c5e81e672699e0c5557b2b755cc8f7a69aa92bff
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39836.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39836
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
