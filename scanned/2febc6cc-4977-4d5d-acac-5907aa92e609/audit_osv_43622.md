# [H] wifi: mwifiex: use the subframe length when parsing A-MSDU TDLS frames

## Summary
Severity: High
Advisory: CVE-2026-74488
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74488
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mwifiex: use the subframe length when parsing A-MSDU TDLS frames

mwifiex_11n_dispatch_amsdu_pkt() splits an A-MSDU with
ieee80211_amsdu_to_8023s() and walks the resulting subframes. For each
subframe it passes the subframe data pointer to
mwifiex_process_tdls_action_frame(), but pairs it with skb->len, the
length of the A-MSDU parent, instead of rx_skb->len:

	rx_skb = __skb_dequeue(&list);
	rx_hdr = (struct rx_packet_hdr *)rx_skb->data;
	if (ISSUPP_TDLS_ENABLED(priv->adapter->fw_cap_info) &&
	    ntohs(rx_hdr->eth803_hdr.h_proto) == ETH_P_TDLS) {
		mwifiex_process_tdls_action_frame(priv, (u8 *)rx_hdr,
						  skb->len);
	}

The parent is not a valid description of that buffer, and may not be
valid memory at all. ieee80211_amsdu_to_8023s() ends with

	if (!reuse_skb)
		dev_kfree_skb(skb);

and it only sets reuse_skb when the parent is linear, is not a
head_frag, and is being consumed as the *last* subframe. So when the
parent does not qualify for reuse it has already been freed, and the
read of skb->len is a use-after-free. When it is reused, skb->len is
the length of the last subframe, applied to every earlier subframe,
which over-states the buffer whenever an earlier subframe is shorter.

The callee cannot absorb a wrong length, because it derives its own
ceiling from the value it is given. Each frame type computes

	ies_len = len - sizeof(struct ethhdr) - TDLS_*_FIX_LEN;

and the element walk is then bounded entirely against that ceiling,

	for (end = pos + ies_len; pos + 1 < end; pos += 2 + pos[1]) {
		u8 ie_len = pos[1];

		if (pos + 2 + ie_len > end)
			break;

so a too-large len moves end past the end of the subframe and the walk
reads and copies beyond it. The A-MSDU layout is chosen by the sender,
which makes the difference between the last subframe and a shorter
earlier one remotely selectable. Reaching this requires TDLS support in
firmware and the TDLS ethertype on the subframe.

The other caller, mwifiex_process_rx_packet(), is correct: it passes a
pointer and a length that describe the same region of the RX buffer.

Pass rx_skb->len, the length of the subframe actually being parsed.

## References
- https://git.kernel.org/stable/c/25e5a3fe4f15e30f74eca42cbf3bcc3a3fbeda79
- https://git.kernel.org/stable/c/3b02275833a0d3e6583627995d614fa99bdf364f
- https://git.kernel.org/stable/c/5a21ab03829cb6d2682c127f22e2b9cd63b4393f
- https://git.kernel.org/stable/c/707664027bb9307f7268eda403af7c4ccd9b8644
- https://git.kernel.org/stable/c/99a948382af8a225e2d5e54a7052158cd6281cc6
- https://git.kernel.org/stable/c/a1f0f7dc7eb15754e6931b433edb7beb754c996a
- https://git.kernel.org/stable/c/c9dcfe6b8b71369e1d732e2ff622c3696a2f032c
- https://git.kernel.org/stable/c/ece2ebb34247d573142617dfc534a9dc11ba59be
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74488.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74488
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
