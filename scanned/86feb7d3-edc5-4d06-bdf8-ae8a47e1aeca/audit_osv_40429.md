# [H] io_uring/net: inherit IORING_CQE_F_BUF_MORE across bundle recv retries

## Summary
Severity: High
Advisory: CVE-2026-53191
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53191
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/net: inherit IORING_CQE_F_BUF_MORE across bundle recv retries

When a bundle recv retries inside io_recv_finish(), the merge logic OR
the saved cflags from the previous iteration with the cflags returned by
the new iteration:
  cflags = req->cqe.flags | (cflags & CQE_F_MASK);

Bits listed in CQE_F_MASK are inherited from the new iteration, and all
other bits (notably IORING_CQE_F_BUFFER and the buffer ID) come from the
saved cflags. Before this change CQE_F_MASK covered only
IORING_CQE_F_SOCK_NONEMPTY and IORING_CQE_F_MORE.

When using provided buffer rings (IOU_PBUF_RING_INC) with incremental
mode, and bundle recv, io_kbuf_inc_commit() can leave the head ring
entry partially consumed, __io_put_kbufs() then sets
IORING_CQE_F_BUF_MORE on the returned cflags so userspace knows the
buffer ID will be reused for subsequent completions.

Because IORING_CQE_F_BUF_MORE was not in CQE_F_MASK, the merge above
silently dropped it whenever the final retry iteration partially
consumed the buffer, and the subsequent req->cqe.flags = cflags &
~CQE_F_MASK save would have left a stale IORING_CQE_F_BUF_MORE in the
carried-over cflags had one been present. Userspace would then
wrongfully advance it ring head past an entry the kernel still uses.

Add IORING_CQE_F_BUF_MORE to CQE_F_MASK so it is both inherited from the
new iteration into the user-visible CQE and stripped from the saved
cflags between iterations.

## References
- https://git.kernel.org/stable/c/0bbc9481f970b0b4ddb08cfa464db1cc93b74b56
- https://git.kernel.org/stable/c/4973232a67e4137ab9399f504f7f2bdd847f96d2
- https://git.kernel.org/stable/c/ed46f39c47eb5530a9c161481a2080d3a869cfaf
- https://git.kernel.org/stable/c/f40570fda3f3a1f96aeaa4aef665ba274b2810b5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53191.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53191
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
