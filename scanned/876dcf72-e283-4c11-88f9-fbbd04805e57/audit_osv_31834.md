# [M] sockmap, vsock: For connectible sockets allow only connected

## Summary
Severity: Medium
Advisory: CVE-2025-21854
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-12
Source: https://osv.dev/vulnerability/CVE-2025-21854
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.80, >=6.7.0 <6.12.17, >=6.13.0 <6.13.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

sockmap, vsock: For connectible sockets allow only connected

sockmap expects all vsocks to have a transport assigned, which is expressed
in vsock_proto::psock_update_sk_prot(). However, there is an edge case
where an unconnected (connectible) socket may lose its previously assigned
transport. This is handled with a NULL check in the vsock/BPF recv path.

Another design detail is that listening vsocks are not supposed to have any
transport assigned at all. Which implies they are not supported by the
sockmap. But this is complicated by the fact that a socket, before
switching to TCP_LISTEN, may have had some transport assigned during a
failed connect() attempt. Hence, we may end up with a listening vsock in a
sockmap, which blows up quickly:

KASAN: null-ptr-deref in range [0x0000000000000120-0x0000000000000127]
CPU: 7 UID: 0 PID: 56 Comm: kworker/7:0 Not tainted 6.14.0-rc1+
Workqueue: vsock-loopback vsock_loopback_work
RIP: 0010:vsock_read_skb+0x4b/0x90
Call Trace:
 sk_psock_verdict_data_ready+0xa4/0x2e0
 virtio_transport_recv_pkt+0x1ca8/0x2acc
 vsock_loopback_work+0x27d/0x3f0
 process_one_work+0x846/0x1420
 worker_thread+0x5b3/0xf80
 kthread+0x35a/0x700
 ret_from_fork+0x2d/0x70
 ret_from_fork_asm+0x1a/0x30

For connectible sockets, instead of relying solely on the state of
vsk->transport, tell sockmap to only allow those representing established
connections. This aligns with the behaviour for AF_INET and AF_UNIX.

## References
- https://git.kernel.org/stable/c/22b683217ad2112791a708693cb236507abd637a
- https://git.kernel.org/stable/c/8fb5bb169d17cdd12c2dcc2e96830ed487d77a0f
- https://git.kernel.org/stable/c/cc9a7832ede53ade1ba9991f0e27314caa4029d8
- https://git.kernel.org/stable/c/f7b473e35986835cc2813fef7b9d40336a09247e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21854.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21854
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
