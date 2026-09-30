# [H] nilfs2: fix WARNING in mark_buffer_dirty due to discarded buffer reuse

## Summary
Severity: High
Advisory: CVE-2023-54140
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54140
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <4.14.326, >=4.15.0 <4.19.295, >=4.20.0 <5.4.257, >=5.5.0 <5.10.195, >=5.11.0 <5.15.131, >=5.16.0 <6.1.52, >=6.2.0 <6.4.15, >=6.5.0 <6.5.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix WARNING in mark_buffer_dirty due to discarded buffer reuse

A syzbot stress test using a corrupted disk image reported that
mark_buffer_dirty() called from __nilfs_mark_inode_dirty() or
nilfs_palloc_commit_alloc_entry() may output a kernel warning, and can
panic if the kernel is booted with panic_on_warn.

This is because nilfs2 keeps buffer pointers in local structures for some
metadata and reuses them, but such buffers may be forcibly discarded by
nilfs_clear_dirty_page() in some critical situations.

This issue is reported to appear after commit 28a65b49eb53 ("nilfs2: do
not write dirty data after degenerating to read-only"), but the issue has
potentially existed before.

Fix this issue by checking the uptodate flag when attempting to reuse an
internally held buffer, and reloading the metadata instead of reusing the
buffer if the flag was lost.

## References
- https://git.kernel.org/stable/c/46c11be2dca295742a5508ea910a77f7733fb7f4
- https://git.kernel.org/stable/c/473795610594f261e98920f0945550314df36f07
- https://git.kernel.org/stable/c/4da07e958bfda2d69d83db105780e8916e3ac02e
- https://git.kernel.org/stable/c/99a73016a5e12a09586a96f998e91f9ea145cd00
- https://git.kernel.org/stable/c/b308b3eabc429649b5501d36290cea403fbd746c
- https://git.kernel.org/stable/c/b911bef132a06de01a745c6a24172d6db7216333
- https://git.kernel.org/stable/c/cdaac8e7e5a059f9b5e816cda257f08d0abffacd
- https://git.kernel.org/stable/c/d95e403588738c7ec38f52b9f490b15e7745d393
- https://git.kernel.org/stable/c/f1d637b63d8a27ac3386f186a694907f2717fc13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54140.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54140
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
