# [H] Bluetooth: ISO: fix UAF in iso_recv_frame

## Summary
Severity: High
Advisory: CVE-2026-63946
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63946
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: ISO: fix UAF in iso_recv_frame

iso_recv_frame reads conn->sk under iso_conn_lock but releases the lock
before using sk, with no reference held. A concurrent iso_sock_kill()
can free sk in that window, causing use-after-free on sk->sk_state and
sock_queue_rcv_skb().

Fix by replacing the bare pointer read with iso_sock_hold(conn), which
calls sock_hold() while the spinlock is held, atomically elevating the
refcount before the lock drops. Add a drop_put label so sock_put() is
called on all exit paths where the hold succeeded.

## References
- https://git.kernel.org/stable/c/119fb6f80c44dc1c65d604cf28e64c56bd9b6568
- https://git.kernel.org/stable/c/1a6b803b00ccdd7666506adbe01ddae1c72d1ca9
- https://git.kernel.org/stable/c/47f23a259517abbdb8032c057a1e8a6bf3734878
- https://git.kernel.org/stable/c/b04ec131325baf4ea4577d6c6e6b86cf092e3731
- https://git.kernel.org/stable/c/c318aa51830a3d2cc1229968fe521441c97356cd
- https://git.kernel.org/stable/c/c57ea90f203c8b8b41a474f19a09000d0f841436
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63946.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63946
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
