# [H] wifi: mac80211: capture fast-RX rate before mesh reuses skb->cb

## Summary
Severity: High
Advisory: CVE-2026-64117
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64117
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: capture fast-RX rate before mesh reuses skb->cb

ieee80211_invoke_fast_rx() reads RX status through
IEEE80211_SKB_RXCB(skb), which aliases the same skb->cb storage
that ieee80211_rx_mesh_data() reuses as IEEE80211_TX_INFO.  In the
unicast forward path, mesh_data does:

	info = IEEE80211_SKB_CB(fwd_skb);
	memset(info, 0, sizeof(*info));

on the same skb the caller still names via rx->skb, then either
queues the skb for TX (success) or kfree_skb()'s it (no-route)
before returning RX_QUEUED.  The caller's RX_QUEUED arm then
calls sta_stats_encode_rate(status) on memory that is either
zeroed (success path) or freed (no-route path).  The latter is
KASAN slab-use-after-free in ieee80211_prepare_and_rx_handle.

Fix by encoding the rate from status before invoking
ieee80211_rx_mesh_data(), so the RX_QUEUED arm consumes a value
captured while status was still backed by valid memory.

## References
- https://git.kernel.org/stable/c/2fb64f94f9afb774f2fa0c7835727d7a67f89f07
- https://git.kernel.org/stable/c/d71c841be5d9e586ee7f36c0dc8ed4db0d9a1349
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64117.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64117
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
