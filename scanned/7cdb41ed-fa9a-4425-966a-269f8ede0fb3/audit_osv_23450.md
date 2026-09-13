# [H] misc: fastrpc: avoid double fput() on failed usercopy

## Summary
Severity: High
Advisory: CVE-2022-48821
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2022-48821
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.180, >=5.5.0 <5.10.101, >=5.11.0 <5.15.24, >=5.16.0 <5.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: fastrpc: avoid double fput() on failed usercopy

If the copy back to userland fails for the FASTRPC_IOCTL_ALLOC_DMA_BUFF
ioctl(), we shouldn't assume that 'buf->dmabuf' is still valid. In fact,
dma_buf_fd() called fd_install() before, i.e. "consumed" one reference,
leaving us with none.

Calling dma_buf_put() will therefore put a reference we no longer own,
leading to a valid file descritor table entry for an already released
'file' object which is a straight use-after-free.

Simply avoid calling dma_buf_put() and rely on the process exit code to
do the necessary cleanup, if needed, i.e. if the file descriptor is
still valid.

## References
- https://git.kernel.org/stable/c/46963e2e0629cb31c96b1d47ddd89dc3d8990b34
- https://git.kernel.org/stable/c/4e6fd2b5fcf8e7119305a6042bd92e7f2b9ed215
- https://git.kernel.org/stable/c/76f85c307ef9f10aa2cef1b1d5ee654c1f3345fc
- https://git.kernel.org/stable/c/a5ce7ee5fcc07583159f54ab4af5164de00148f5
- https://git.kernel.org/stable/c/e4382d0a39f9a1e260d62fdc079ddae5293c037d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48821.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48821
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
