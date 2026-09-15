# [H] fbdev: udlfb: add vm_ops to dlfb_ops_mmap to prevent use-after-free

## Summary
Severity: High
Advisory: CVE-2026-43497
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-21
Source: https://osv.dev/vulnerability/CVE-2026-43497
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

fbdev: udlfb: add vm_ops to dlfb_ops_mmap to prevent use-after-free

dlfb_ops_mmap() uses remap_pfn_range() to map vmalloc framebuffer pages
to userspace but sets no vm_ops on the VMA. This means the kernel cannot
track active mmaps. When dlfb_realloc_framebuffer() replaces the backing
buffer via FBIOPUT_VSCREENINFO, existing mmap PTEs are not invalidated.
On USB disconnect, dlfb_ops_destroy() calls vfree() on the old pages
while userspace PTEs still reference them, resulting in a use-after-free:
the process retains read/write access to freed kernel pages.

Add vm_operations_struct with open/close callbacks that maintain an
atomic mmap_count on struct dlfb_data. In dlfb_realloc_framebuffer(),
check mmap_count and return -EBUSY if the buffer is currently mapped,
preventing buffer replacement while userspace holds stale PTEs.

Tested with PoC using dummy_hcd + raw_gadget USB device emulation.

## References
- https://git.kernel.org/stable/c/18dd358de72d57993422cbb5dfb29ccd74efe192
- https://git.kernel.org/stable/c/4f312c30f0368e8d2a76aa650dff73f23490b5e7
- https://git.kernel.org/stable/c/5931f5651ee32bd41b3323256b31fcc8e71336ed
- https://git.kernel.org/stable/c/60f711cfd580f86fea8284146ac133804e728f9a
- https://git.kernel.org/stable/c/8de779dc40d35d39fa07387b6f921eb11df0f511
- https://git.kernel.org/stable/c/a2c53a3822ee26e8d758071815b9ed3bf6669fc1
- https://git.kernel.org/stable/c/da9b065cedfd3b574f229d5be594e6aa47a27ae6
- https://git.kernel.org/stable/c/e3d9865dacd7435b8465848428210d0f0c673311
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43497.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43497
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
