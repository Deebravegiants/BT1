# [H] netfilter: bridge: replace physindev with physinif in nf_bridge_info

## Summary
Severity: High
Advisory: CVE-2024-35839
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35839
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <6.1.75, >=6.2.0 <6.6.14, >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: bridge: replace physindev with physinif in nf_bridge_info

An skb can be added to a neigh->arp_queue while waiting for an arp
reply. Where original skb's skb->dev can be different to neigh's
neigh->dev. For instance in case of bridging dnated skb from one veth to
another, the skb would be added to a neigh->arp_queue of the bridge.

As skb->dev can be reset back to nf_bridge->physindev and used, and as
there is no explicit mechanism that prevents this physindev from been
freed under us (for instance neigh_flush_dev doesn't cleanup skbs from
different device's neigh queue) we can crash on e.g. this stack:

arp_process
  neigh_update
    skb = __skb_dequeue(&neigh->arp_queue)
      neigh_resolve_output(..., skb)
        ...
          br_nf_dev_xmit
            br_nf_pre_routing_finish_bridge_slow
              skb->dev = nf_bridge->physindev
              br_handle_frame_finish

Let's use plain ifindex instead of net_device link. To peek into the
original net_device we will use dev_get_by_index_rcu(). Thus either we
get device and are safe to use it or we don't get it and drop skb.

## References
- https://git.kernel.org/stable/c/544add1f1cfb78c3dfa3e6edcf4668f6be5e730c
- https://git.kernel.org/stable/c/7ae19ee81ca56b13c50a78de6c47d5b8fdc9d97b
- https://git.kernel.org/stable/c/9325e3188a9cf3f69fc6f32af59844bbc5b90547
- https://git.kernel.org/stable/c/9874808878d9eed407e3977fd11fee49de1e1d86
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35839.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35839
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
