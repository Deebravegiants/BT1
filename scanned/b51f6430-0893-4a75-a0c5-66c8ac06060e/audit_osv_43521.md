# [C] vhost/net: complete zerocopy ubufs only once

## Summary
Severity: Critical
Advisory: CVE-2026-74310
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74310
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.1.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

vhost/net: complete zerocopy ubufs only once

vhost-net initializes one ubuf_info per outstanding zerocopy TX
descriptor and hands it to the backend socket.  The networking stack may
then clone a zerocopy skb before all skb references are released.  For
example, batman-adv fragmentation reaches skb_split(), which calls
skb_zerocopy_clone() and increments the same ubuf_info refcount.

vhost_zerocopy_complete() currently treats every ubuf callback as a
completed vhost descriptor.  It dereferences ubuf->ctx, writes the
descriptor completion state, and drops the vhost_net_ubuf_ref even when
the callback only releases a cloned skb reference.  A backend reset can
therefore wait for and free the vhost_net_ubuf_ref while another cloned
skb still carries the same ubuf_info.  A later completion then
dereferences the freed ubufs pointer.

KASAN reports the stale completion as:

  BUG: KASAN: slab-use-after-free in vhost_zerocopy_complete+0x1d7/0x1f0
  BUG: KASAN: slab-use-after-free in vhost_zerocopy_complete+0x101/0x1f0
  vhost_zerocopy_complete
  skb_copy_ubufs
  __dev_forward_skb2
  veth_xmit

The freed object was allocated from vhost_net_ioctl() while setting the
backend and freed through kfree_rcu()/kvfree_rcu_bulk after backend
removal, while delayed skb completion still reached
vhost_zerocopy_complete().

Honor the generic ubuf_info refcount before touching vhost state, and run
the vhost descriptor completion only for the final ubuf reference.  This
matches the msg_zerocopy_complete() ownership rule for cloned zerocopy
skbs.

## References
- https://git.kernel.org/stable/c/321c73baf54d971ce3771fea275c98a247f7ee35
- https://git.kernel.org/stable/c/6445b945024f4c7675ae5352b2d5885cb1deea71
- https://git.kernel.org/stable/c/8f6898fe80794f2d7c3d38c1158c806e4074a1c4
- https://git.kernel.org/stable/c/a9f8a1d2e3ff511eafd4c5462481950c2f4d2b5d
- https://git.kernel.org/stable/c/c069437924663539a93a1e5afe90838d9ccee284
- https://git.kernel.org/stable/c/ea71f873423fb73e66ad88936d6759ac0ad4aa53
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74310.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74310
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
