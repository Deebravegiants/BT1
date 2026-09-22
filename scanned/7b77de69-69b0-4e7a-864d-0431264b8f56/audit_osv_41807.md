# [H] xfrm: route MIGRATE notifications to caller's netns

## Summary
Severity: High
Advisory: CVE-2026-63914
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:L)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63914
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.21 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: route MIGRATE notifications to caller's netns

xfrm_send_migrate() in net/xfrm/xfrm_user.c and pfkey_send_migrate()
in net/key/af_key.c both hardcode &init_net for the multicast that
announces a successful XFRM_MSG_MIGRATE / SADB_X_MIGRATE.

XFRM_MSG_MIGRATE arrives on a per-netns NETLINK_XFRM socket, and the
rest of the xfrm/af_key netlink path was made netns-aware in 2008.
The other 14 multicast paths in xfrm_user.c route their event using
xs_net(x), xp_net(xp) or sock_net(skb->sk); only the migrate path
was missed.

Two consequences of the init_net hardcoding:

  1. The notification (selector, old/new endpoint addresses, and the
     km_address) is delivered to listeners on init_net's
     XFRMNLGRP_MIGRATE / pfkey BROADCAST_ALL groups rather than on
     the issuing netns. An IKE daemon running in init_net therefore
     receives migration notifications originating from any other
     netns on the host.

  2. An IKE daemon running inside a non-init netns and subscribed
     to its own XFRMNLGRP_MIGRATE / pfkey groups never receives the
     notification of its own migration. IKEv2 MOBIKE / address-update
     handling inside a netns is silently broken.

Thread struct net through km_migrate() and the xfrm_mgr.migrate
function pointer, drop the &init_net override in xfrm_send_migrate()
and pfkey_send_migrate(), and pass the caller's net (already in
scope in xfrm_migrate() via sock_net(skb->sk)) all the way down.
struct xfrm_mgr is in-tree only and not exported as a stable API,
so the function-pointer signature change is internal.

pfkey_broadcast() is already netns-aware via net_generic(net,
pfkey_net_id) since the pernet conversion. The five other
pfkey_broadcast() callers in af_key.c already pass xs_net(x),
sock_net(sk) or a per-netns net, so this only removes the
&init_net outlier.

## References
- https://git.kernel.org/stable/c/00f2c451e57df50b1151d9b2254878f106b7c892
- https://git.kernel.org/stable/c/26ce8dbf2e23fe4fcc3351d19ef6d3fb703ed126
- https://git.kernel.org/stable/c/448bb92ca101dde8a6e88b4dc824044b4e341604
- https://git.kernel.org/stable/c/6df8157547347b5257bf640a0ae3dfc4411e06cd
- https://git.kernel.org/stable/c/7e2a4f7ca0952820731ef7bdadfc9a9e9d3571b4
- https://git.kernel.org/stable/c/a306cf2ac8849c487791369fad6f216399d000f6
- https://git.kernel.org/stable/c/bafc7d0774b9bf52909c70ed990bc5ccf7ec4bad
- https://git.kernel.org/stable/c/fe463798343382c8fe9416a95959f005a3c30aa5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63914.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63914
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
