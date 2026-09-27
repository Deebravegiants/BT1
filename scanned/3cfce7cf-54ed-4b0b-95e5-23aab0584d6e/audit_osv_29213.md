# [C] tipc: force a dst refcount before doing decryption

## Summary
Severity: Critical
Advisory: CVE-2024-40983
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40983
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.96, >=6.2.0 <6.6.36, >=6.7.0 <6.9.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: force a dst refcount before doing decryption

As it says in commit 3bc07321ccc2 ("xfrm: Force a dst refcount before
entering the xfrm type handlers"):

"Crypto requests might return asynchronous. In this case we leave the
 rcu protected region, so force a refcount on the skb's destination
 entry before we enter the xfrm type input/output handlers."

On TIPC decryption path it has the same problem, and skb_dst_force()
should be called before doing decryption to avoid a possible crash.

Shuang reported this issue when this warning is triggered:

  [] WARNING: include/net/dst.h:337 tipc_sk_rcv+0x1055/0x1ea0 [tipc]
  [] Kdump: loaded Tainted: G W --------- - - 4.18.0-496.el8.x86_64+debug
  [] Workqueue: crypto cryptd_queue_worker
  [] RIP: 0010:tipc_sk_rcv+0x1055/0x1ea0 [tipc]
  [] Call Trace:
  [] tipc_sk_mcast_rcv+0x548/0xea0 [tipc]
  [] tipc_rcv+0xcf5/0x1060 [tipc]
  [] tipc_aead_decrypt_done+0x215/0x2e0 [tipc]
  [] cryptd_aead_crypt+0xdb/0x190
  [] cryptd_queue_worker+0xed/0x190
  [] process_one_work+0x93d/0x17e0

## References
- https://git.kernel.org/stable/c/2ebe8f840c7450ecbfca9d18ac92e9ce9155e269
- https://git.kernel.org/stable/c/3eb1b39627892c4e26cb0162b75725aa5fcc60c8
- https://git.kernel.org/stable/c/623c90d86a61e3780f682b32928af469c66ec4c2
- https://git.kernel.org/stable/c/6808b41371670c51feea14f63ade211e78100930
- https://git.kernel.org/stable/c/692803b39a36e63ac73208e0a3769ae6a2f9bc76
- https://git.kernel.org/stable/c/b57a4a2dc8746cea58a922ebe31b6aa629d69d93
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40983.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40983
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
