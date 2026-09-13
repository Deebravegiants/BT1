# [H] tipc: move bc link creation back to tipc_node_create

## Summary
Severity: High
Advisory: CVE-2022-49664
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49664
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.129, >=5.11.0 <5.15.53, >=5.16.0 <5.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: move bc link creation back to tipc_node_create

Shuang Li reported a NULL pointer dereference crash:

  [] BUG: kernel NULL pointer dereference, address: 0000000000000068
  [] RIP: 0010:tipc_link_is_up+0x5/0x10 [tipc]
  [] Call Trace:
  []  <IRQ>
  []  tipc_bcast_rcv+0xa2/0x190 [tipc]
  []  tipc_node_bc_rcv+0x8b/0x200 [tipc]
  []  tipc_rcv+0x3af/0x5b0 [tipc]
  []  tipc_udp_recv+0xc7/0x1e0 [tipc]

It was caused by the 'l' passed into tipc_bcast_rcv() is NULL. When it
creates a node in tipc_node_check_dest(), after inserting the new node
into hashtable in tipc_node_create(), it creates the bc link. However,
there is a gap between this insert and bc link creation, a bc packet
may come in and get the node from the hashtable then try to dereference
its bc link, which is NULL.

This patch is to fix it by moving the bc link creation before inserting
into the hashtable.

Note that for a preliminary node becoming "real", the bc link creation
should also be called before it's rehashed, as we don't create it for
preliminary nodes.

## References
- https://git.kernel.org/stable/c/35fcb2ba35b4d9b592b558c3bcc6e0d90e213588
- https://git.kernel.org/stable/c/456bc338871c4a52117dd5ef29cce3745456d248
- https://git.kernel.org/stable/c/cb8092d70a6f5f01ec1490fce4d35efed3ed996c
- https://git.kernel.org/stable/c/e52910e671f58c619e33dac476b11b35e2d3ab6f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49664.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49664
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
