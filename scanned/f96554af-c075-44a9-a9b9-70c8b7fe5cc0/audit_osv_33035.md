# [H] xen: fix UAF in dmabuf_exp_from_pages()

## Summary
Severity: High
Advisory: CVE-2025-38595
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38595
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

xen: fix UAF in dmabuf_exp_from_pages()

[dma_buf_fd() fixes; no preferences regarding the tree it goes through -
up to xen folks]

As soon as we'd inserted a file reference into descriptor table, another
thread could close it.  That's fine for the case when all we are doing is
returning that descriptor to userland (it's a race, but it's a userland
race and there's nothing the kernel can do about it).  However, if we
follow fd_install() with any kind of access to objects that would be
destroyed on close (be it the struct file itself or anything destroyed
by its ->release()), we have a UAF.

dma_buf_fd() is a combination of reserving a descriptor and fd_install().
gntdev dmabuf_exp_from_pages() calls it and then proceeds to access the
objects destroyed on close - starting with gntdev_dmabuf itself.

Fix that by doing reserving descriptor before anything else and do
fd_install() only when everything had been set up.

## References
- https://git.kernel.org/stable/c/3edfd2353f301bfffd5ee41066e37320a59ccc2d
- https://git.kernel.org/stable/c/532c8b51b3a8676cbf533a291f8156774f30ea87
- https://git.kernel.org/stable/c/d59d49af4aeed9a81e673e37c26c6a3bacf1a181
- https://git.kernel.org/stable/c/e5907885260401bba300d4d18d79875c05b82651
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38595.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38595
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
