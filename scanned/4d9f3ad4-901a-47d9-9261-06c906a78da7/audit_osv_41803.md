# [H] dma-buf: fix UAF in dma_buf_fd() tracepoint

## Summary
Severity: High
Advisory: CVE-2026-63910
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63910
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

dma-buf: fix UAF in dma_buf_fd() tracepoint

Once FD_ADD() returns, the fd is live in the file descriptor table
and a thread sharing that table can close() it before DMA_BUF_TRACE()
runs. The close drops the last reference, __fput() frees the dma_buf,
and the tracepoint then dereferences dmabuf to take dmabuf->name_lock
-- slab-use-after-free.

Split FD_ADD() back into get_unused_fd_flags() + fd_install() and
emit the tracepoint between them. While the fdtable slot is reserved
with a NULL file pointer, a racing close() returns -EBADF without
entering __fput(), so the dma_buf stays alive across the trace. Same
approach as commit 2d76319c4cbb ("dma-buf: fix UAF in dma_buf_put()
tracepoint").

This undoes the FD_ADD() conversion done in commit 34dfce523c90
("dma: convert dma_buf_fd() to FD_ADD()"); FD_ADD() has no place to
hook the tracepoint safely.

## References
- https://git.kernel.org/stable/c/b569f86e2f8dbf6f11d31d3de794d22e18098b23
- https://git.kernel.org/stable/c/ead6680f354f83966c796fc7f9463a3171789616
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63910.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63910
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
