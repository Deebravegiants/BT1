# [C] netfilter: nf_nat_sip: reload possible stale data pointer

## Summary
Severity: Critical
Advisory: CVE-2026-72251
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72251
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.9.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_nat_sip: reload possible stale data pointer

quoting sashiko:
 ------------------------------------------------------------------------
 [..] noticed a potential memory bug and header corruption involving the
 SIP NAT helper.

 In net/netfilter/nf_nat_sip.c:nf_nat_sip():
	if (skb_ensure_writable(skb, skb->len)) {
		nf_ct_helper_log(skb, ct, "cannot mangle packet");
		return NF_DROP;
	}
	uh = (void *)skb->data + protoff;
	uh->dest = ct_sip_info->forced_dport;
	if (!nf_nat_mangle_udp_packet(skb, ct, ctinfo, protoff,
				      0, 0, NULL, 0)) {

 If a cloned or fragmented SKB is reallocated by skb_ensure_writable(), the
 old data buffer is freed. However, nf_nat_sip() fails to update *dptr to
 point to the new buffer.

 It also appears to use nf_nat_mangle_udp_packet() on what could be a TCP
 packet, which would overwrite the sequence number with a checksum update.
 ------------------------------------------------------------------------

nf_conntrack_sip linerizes skbs, hence no fragmented skb can be seen.
But clones are possible, so rebuild dptr.

Disable nf_nat_mangle_udp_packet() branch for TCP streams.
It doesn't look like this can ever happen, else we should have received
bug reports about this, so just check the conntrack is UDP and drop
otherwise.

The calling conntrack_sip set ->forced_dport for SIP_HDR_VIA_UDP messages,
so I don't think this is ever expected to be true for a TCP stream.

## References
- https://git.kernel.org/stable/c/0e76e3e886cc9ee027337d5ad39cb96f57b7bdc7
- https://git.kernel.org/stable/c/2bcf2c5052fb5e73e255140ab43f056aef409c27
- https://git.kernel.org/stable/c/57e4e29644ec054d7021d296407e7ddd844afea2
- https://git.kernel.org/stable/c/77e43bcb7ec177e293a5c3f1b91a2c5aebfb6c68
- https://git.kernel.org/stable/c/bded21a4bf9bf86a79148be735723a97ca9a7532
- https://git.kernel.org/stable/c/dc11f26685aa850f237226f0f463647aea58ab7c
- https://git.kernel.org/stable/c/e38143c9b477f2968024c47c647dd4456a40aff1
- https://git.kernel.org/stable/c/eae9c6ccb5af69c713a65f8ae219f5c1aa32cd17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72251.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72251
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
