# [C] tipc: fix UAF in tipc_l2_send_msg()

## Summary
Severity: Critical
Advisory: CVE-2026-74255
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74255
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: fix UAF in tipc_l2_send_msg()

Syzbot reported a slab-use-after-free in ipvlan_hard_header() when
called from tipc_l2_send_msg().

The root cause is that tipc_disable_l2_media() calls synchronize_net()
while b->media_ptr is still valid. This allows concurrent RCU readers
to obtain the device pointer after synchronize_net() has finished.
The pointer is cleared later in bearer_disable(), but without any
subsequent synchronization, allowing the device to be freed while
still in use by readers.

Fix this by clearing b->media_ptr in tipc_disable_l2_media() before
calling synchronize_net().

This is safe to do now because the call order in bearer_disable()
was reversed in 0d051bf93c06 ("tipc: make bearer packet filtering generic")
to call tipc_node_delete_links() (which needs the pointer) before
disable_media().

https: //lore.kernel.org/netdev/6a2c1007.428ffe26.258b27.015d.GAE@google.com/T/#u

## References
- https://git.kernel.org/stable/c/0d8a12d7143126afdf9fbe2e3d438650dd6603ed
- https://git.kernel.org/stable/c/35e0297a93c3c34a3924eeef816c03504e3ab5c5
- https://git.kernel.org/stable/c/50ff092633b06382e5091dd5b093ce943d4ac2f9
- https://git.kernel.org/stable/c/609ced2301be1df7e7ed2ef47d1d916674e6ba3b
- https://git.kernel.org/stable/c/71aafa16d79b107b33837f60b6cbc7d0cb8c5708
- https://git.kernel.org/stable/c/aef12b5ce793dea6b3a97a58fd0f946000ae8945
- https://git.kernel.org/stable/c/f4002f1c669cc02e3763f479fc25ff1dfa9e2420
- https://git.kernel.org/stable/c/f4c3d89fc986b0da196ddfc6cfe0ea5d5d08bec6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74255.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74255
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
