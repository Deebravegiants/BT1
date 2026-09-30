# [H] wifi: mac80211: defer link RX stats percpu free to RCU

## Summary
Severity: High
Advisory: CVE-2026-68409
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68409
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: defer link RX stats percpu free to RCU

sta_remove_link() frees a removed MLO link's RX stats percpu buffer right
away, but defers only the link container to RCU:

	sta_info_free_link(&alloc->info);
	kfree_rcu(alloc, rcu_head);

The RX fast path reads link_sta under rcu_read_lock and writes the percpu
stats. A reader that resolved link_sta before the removal keeps the
pointer. The container stays alive from the kfree_rcu, so the read still
works. But the percpu block it points to is already freed. This needs
uses_rss. That is when pcpu_rx_stats exists.

The full STA teardown frees the deflink stats only after
synchronize_net(). The link removal path had no such barrier. The race is
hard to win in practice, but the free should still wait for RCU.

Free the link together with its data from a single RCU callback, so the
percpu block is reclaimed only after readers drain.

## References
- https://git.kernel.org/stable/c/2aa1789880fa5e41049b0f6a74a4fc2fa1997610
- https://git.kernel.org/stable/c/a03fceae0c65b31ce31840dac5e26684ceecb65b
- https://git.kernel.org/stable/c/aa2eb62525188269cdd402a583b9a8ed94657ff0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68409.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68409
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
