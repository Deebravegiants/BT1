# [H] xsk: Fix race condition in AF_XDP generic RX path

## Summary
Severity: High
Advisory: CVE-2025-37920
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37920
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <6.1.164, >=6.2.0 <6.6.123, >=6.7.0 <6.12.28, >=6.13.0 <6.14.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

xsk: Fix race condition in AF_XDP generic RX path

Move rx_lock from xsk_socket to xsk_buff_pool.
Fix synchronization for shared umem mode in
generic RX path where multiple sockets share
single xsk_buff_pool.

RX queue is exclusive to xsk_socket, while FILL
queue can be shared between multiple sockets.
This could result in race condition where two
CPU cores access RX path of two different sockets
sharing the same umem.

Protect both queues by acquiring spinlock in shared
xsk_buff_pool.

Lock contention may be minimized in the future by some
per-thread FQ buffering.

It's safe and necessary to move spin_lock_bh(rx_lock)
after xsk_rcv_check():
* xs->pool and spinlock_init is synchronized by
  xsk_bind() -> xsk_is_bound() memory barriers.
* xsk_rcv_check() may return true at the moment
  of xsk_release() or xsk_unbind_dev(),
  however this will not cause any data races or
  race conditions. xsk_unbind_dev() removes xdp
  socket from all maps and waits for completion
  of all outstanding rx operations. Packets in
  RX path will either complete safely or drop.

## References
- https://git.kernel.org/stable/c/65d3c570614b892257dc58a1b202908242ecf8fd
- https://git.kernel.org/stable/c/75a240a3e8abf17b9e00b0ef0492b1bbaa932251
- https://git.kernel.org/stable/c/975b372313dc018b9bd6cc0d85d188787054b19e
- https://git.kernel.org/stable/c/a1356ac7749cafc4e27aa62c0c4604b5dca4983e
- https://git.kernel.org/stable/c/b6978c565ce33658543c637060852434b4248d30
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37920.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37920
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
