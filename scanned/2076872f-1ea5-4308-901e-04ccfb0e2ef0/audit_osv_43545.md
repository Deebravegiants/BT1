# [H] bpf: Take mmap_lock in zap_pages()

## Summary
Severity: High
Advisory: CVE-2026-74354
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74354
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Take mmap_lock in zap_pages()

zap_vma_range() requires the owning mm's mmap_lock to be held.

Taking mmap_read_lock under arena->lock would AB-BA against
arena_vm_close() and arena_map_mmap(), both of which run with
mmap_write_lock held and then acquire arena->lock. Instead drop
arena->lock, mmget_not_zero() the vma's mm, take mmap_read_lock, and
re-resolve the vma via find_vma() since it may have been unmapped or
replaced while waiting.

Track processed vmls with a per-call generation in vml->zap_gen and
serialize zap_pages() callers with a new arena->zap_mutex so
concurrent callers on different uaddr ranges do not mark each other's
vmls processed before the zap is done.

## References
- https://git.kernel.org/stable/c/36b1d997866f6083d33934983aa2ce0a184ed642
- https://git.kernel.org/stable/c/80b89d0226a05e8b67969de99c31b51fcd54f76a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74354.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74354
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
