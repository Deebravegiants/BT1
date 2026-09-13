# [H] ppp: defer channel free to an RCU grace period to fix pppol2tp RX UAF

## Summary
Severity: High
Advisory: CVE-2026-68398
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68398
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ppp: defer channel free to an RCU grace period to fix pppol2tp RX UAF

pppol2tp_recv() runs in the L2TP UDP-encap softirq RX path:

 l2tp_udp_encap_recv() -> l2tp_recv_common() -> pppol2tp_recv()
   -> ppp_input(&po->chan)

It runs under rcu_read_lock() holding only an l2tp_session reference and
takes NO reference on the internal PPP channel (struct channel,
chan->ppp) that ppp_input() dereferences.

The pppox socket is SOCK_RCU_FREE, so 'po' and the embedded ppp_channel
are RCU-safe.  But the internal struct channel is a separate allocation
that ppp_release_channel() frees with a plain kfree():

 close(data socket) -> pppol2tp_release() -> pppox_unbind_sock()
   -> ppp_unregister_channel() -> ppp_release_channel() -> kfree(pch)

For a channel that is bound (PPPIOCGCHAN) but not attached to a ppp unit
(no PPPIOCCONNECT, pch->ppp == NULL) and not bridged, teardown skips
both ppp_disconnect_channel()'s synchronize_net() and
ppp_unbridge_channels()'s synchronize_rcu(), so the kfree() has no grace
period.  rcu_read_lock() in pppol2tp_recv() does not protect against a
plain kfree(), so an in-flight ppp_input() on one CPU can dereference
the channel just freed by close() on another CPU.

The bug is reachable by an unprivileged user.

Defer the channel free to an RCU callback via call_rcu() so the grace
period fences any in-flight ppp_input(). The disconnect and unbridge
teardown paths already fence with synchronize_net()/synchronize_rcu();
call_rcu() does the same here without stalling the close() path.

## References
- https://git.kernel.org/stable/c/06213c85d8c0994f786c093b8b2a517987943ca6
- https://git.kernel.org/stable/c/110b765744b147c63882f5e9cb12931c5dc8d85f
- https://git.kernel.org/stable/c/3ab32218d7182705dae5c86f13925f458072da2c
- https://git.kernel.org/stable/c/4bb84e964ff0fe0a171c965362de72f9820dbce9
- https://git.kernel.org/stable/c/4e47f1ac188ece11d6fdabe44166a2776cc5bd4e
- https://git.kernel.org/stable/c/c9574b8a8edeb4edd3ac6472c27ef7184bdb2baa
- https://git.kernel.org/stable/c/ec4215683e47424c9c4762fd3c60f552a3119142
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68398.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68398
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
