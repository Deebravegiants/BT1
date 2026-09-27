# [H] ring-buffer: Fix reader locking when changing the sub buffer order

## Summary
Severity: High
Advisory: CVE-2024-50207
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50207
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ring-buffer: Fix reader locking when changing the sub buffer order

The function ring_buffer_subbuf_order_set() updates each
ring_buffer_per_cpu and installs new sub buffers that match the requested
page order. This operation may be invoked concurrently with readers that
rely on some of the modified data, such as the head bit (RB_PAGE_HEAD), or
the ring_buffer_per_cpu.pages and reader_page pointers. However, no
exclusive access is acquired by ring_buffer_subbuf_order_set(). Modifying
the mentioned data while a reader also operates on them can then result in
incorrect memory access and various crashes.

Fix the problem by taking the reader_lock when updating a specific
ring_buffer_per_cpu in ring_buffer_subbuf_order_set().

## References
- https://git.kernel.org/stable/c/09661f75e75cb6c1d2d8326a70c311d46729235f
- https://git.kernel.org/stable/c/a569290525a05162d5dd26d9845591eaf46e5802
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50207.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50207
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
