# [H] io_uring/net: fix slab-out-of-bounds read in io_bundle_nbufs()

## Summary
Severity: High
Advisory: CVE-2026-31774
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31774
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/net: fix slab-out-of-bounds read in io_bundle_nbufs()

sqe->len is __u32 but gets stored into sr->len which is int. When
userspace passes sqe->len values exceeding INT_MAX (e.g. 0xFFFFFFFF),
sr->len overflows to a negative value. This negative value propagates
through the bundle recv/send path:

  1. io_recv(): sel.val = sr->len (ssize_t gets -1)
  2. io_recv_buf_select(): arg.max_len = sel->val (size_t gets
     0xFFFFFFFFFFFFFFFF)
  3. io_ring_buffers_peek(): buf->len is not clamped because max_len
     is astronomically large
  4. iov[].iov_len = 0xFFFFFFFF flows into io_bundle_nbufs()
  5. io_bundle_nbufs(): min_t(int, 0xFFFFFFFF, ret) yields -1,
     causing ret to increase instead of decrease, creating an
     infinite loop that reads past the allocated iov[] array

This results in a slab-out-of-bounds read in io_bundle_nbufs() from
the kmalloc-64 slab, as nbufs increments past the allocated iovec
entries.

  BUG: KASAN: slab-out-of-bounds in io_bundle_nbufs+0x128/0x160
  Read of size 8 at addr ffff888100ae05c8 by task exp/145
  Call Trace:
   io_bundle_nbufs+0x128/0x160
   io_recv_finish+0x117/0xe20
   io_recv+0x2db/0x1160

Fix this by rejecting negative sr->len values early in both
io_sendmsg_prep() and io_recvmsg_prep(). Since sqe->len is __u32,
any value > INT_MAX indicates overflow and is not a valid length.

## References
- https://git.kernel.org/stable/c/1b655cd311344117d3052f6552cb20d9901c9d7c
- https://git.kernel.org/stable/c/90ced24c500ad4e129e9e34b7e56fd7849e350b6
- https://git.kernel.org/stable/c/b948f9d5d3057b01188e36664e7c7604d1c8ecb5
- https://git.kernel.org/stable/c/c314b405dcc4d8b9041124f928f81715d6328bec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31774.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31774
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
