# [H] netfilter: nf_queue: pin bridge device while NFQUEUE holds fake dst

## Summary
Severity: High
Advisory: CVE-2026-72255
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72255
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <5.15.217, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_queue: pin bridge device while NFQUEUE holds fake dst

The br_netfilter fake rtable is embedded in struct net_bridge and is
attached to bridged packets with skb_dst_set_noref(). If such a packet is
queued to NFQUEUE, __nf_queue() upgrades that fake dst with
skb_dst_force().

At that point the queued skb can hold a real dst reference after bridge
teardown has started. The problem is not that every bridged packet needs
its own dst reference. The problem is that NFQUEUE can keep the bridge
private fake dst alive after unregister begins.

Fix this by keeping the bridge fake dst model unchanged and pinning the
bridge master device only while the packet sits in NFQUEUE. Record the
bridge device in nf_queue_entry when the queued skb carries a bridge fake
dst, take a device reference for the queue lifetime, and drop it when the
queue entry is freed.

Also make sure queued entries are reaped when that bridge device goes
down, and drop the redundant nf_bridge_info_exists() test from the fake
dst detection.

This keeps netdev_priv(br->dev) alive until verdict completion, so the
embedded fake rtable and its metrics backing storage cannot be freed out
from under dst_release(). It also avoids the constant refcount bump and
avoids using ipv4-specific dst helpers for IPv6 bridge traffic.

## References
- https://git.kernel.org/stable/c/01ace27af47801dd7f6b839e782b62863af979cc
- https://git.kernel.org/stable/c/0ca505346c5e2905ab7b5313af801fcf38f594a8
- https://git.kernel.org/stable/c/3f03a2d225c668283110ad5f9ff159ba4591e2c7
- https://git.kernel.org/stable/c/430521af7fe8a9c08f5a2554224a35f11f51d99e
- https://git.kernel.org/stable/c/47b3af24de5fbed4bf2952de0f5294ef1a338a26
- https://git.kernel.org/stable/c/8dc51351472825500145eed5bddfb88b2ec32008
- https://git.kernel.org/stable/c/c9c9b37f8c5505224e8d206184df3bb668ee00cf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72255.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72255
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
