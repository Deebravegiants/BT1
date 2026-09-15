# [M] net: fix memory leak in tcp_conn_request()

## Summary
Severity: Medium
Advisory: CVE-2024-57841
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-15
Source: https://osv.dev/vulnerability/CVE-2024-57841
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.176, >=5.16.0 <6.1.124, >=6.2.0 <6.6.70, >=6.7.0 <6.12.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: fix memory leak in tcp_conn_request()

If inet_csk_reqsk_queue_hash_add() return false, tcp_conn_request() will
return without free the dst memory, which allocated in af_ops->route_req.

Here is the kmemleak stack:

unreferenced object 0xffff8881198631c0 (size 240):
  comm "softirq", pid 0, jiffies 4299266571 (age 1802.392s)
  hex dump (first 32 bytes):
    00 10 9b 03 81 88 ff ff 80 98 da bc ff ff ff ff  ................
    81 55 18 bb ff ff ff ff 00 00 00 00 00 00 00 00  .U..............
  backtrace:
    [<ffffffffb93e8d4c>] kmem_cache_alloc+0x60c/0xa80
    [<ffffffffba11b4c5>] dst_alloc+0x55/0x250
    [<ffffffffba227bf6>] rt_dst_alloc+0x46/0x1d0
    [<ffffffffba23050a>] __mkroute_output+0x29a/0xa50
    [<ffffffffba23456b>] ip_route_output_key_hash+0x10b/0x240
    [<ffffffffba2346bd>] ip_route_output_flow+0x1d/0x90
    [<ffffffffba254855>] inet_csk_route_req+0x2c5/0x500
    [<ffffffffba26b331>] tcp_conn_request+0x691/0x12c0
    [<ffffffffba27bd08>] tcp_rcv_state_process+0x3c8/0x11b0
    [<ffffffffba2965c6>] tcp_v4_do_rcv+0x156/0x3b0
    [<ffffffffba299c98>] tcp_v4_rcv+0x1cf8/0x1d80
    [<ffffffffba239656>] ip_protocol_deliver_rcu+0xf6/0x360
    [<ffffffffba2399a6>] ip_local_deliver_finish+0xe6/0x1e0
    [<ffffffffba239b8e>] ip_local_deliver+0xee/0x360
    [<ffffffffba239ead>] ip_rcv+0xad/0x2f0
    [<ffffffffba110943>] __netif_receive_skb_one_core+0x123/0x140

Call dst_release() to free the dst memory when
inet_csk_reqsk_queue_hash_add() return false in tcp_conn_request().

## References
- https://git.kernel.org/stable/c/2af69905180b3fea12f9c1db374b153a06977021
- https://git.kernel.org/stable/c/4f4aa4aa28142d53f8b06585c478476cfe325cfc
- https://git.kernel.org/stable/c/9d38959677291552d1b0ed2689a540af279b5bf8
- https://git.kernel.org/stable/c/b0b190218c78d8aeecfba36ea3a90063b3ede52d
- https://git.kernel.org/stable/c/de3f999bf8aee16e9da1c1224191abdc69e97c9d
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57841.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57841
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
