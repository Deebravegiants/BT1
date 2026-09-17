# [H] ip_gre: test csum_start instead of transport header

## Summary
Severity: High
Advisory: CVE-2022-49340
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49340
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.15.0 <5.17.15, >=5.16.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ip_gre: test csum_start instead of transport header

GRE with TUNNEL_CSUM will apply local checksum offload on
CHECKSUM_PARTIAL packets.

ipgre_xmit must validate csum_start after an optional skb_pull,
else lco_csum may trigger an overflow. The original check was

	if (csum && skb_checksum_start(skb) < skb->data)
		return -EINVAL;

This had false positives when skb_checksum_start is undefined:
when ip_summed is not CHECKSUM_PARTIAL. A discussed refinement
was straightforward

	if (csum && skb->ip_summed == CHECKSUM_PARTIAL &&
	    skb_checksum_start(skb) < skb->data)
		return -EINVAL;

But was eventually revised more thoroughly:
- restrict the check to the only branch where needed, in an
  uncommon GRE path that uses header_ops and calls skb_pull.
- test skb_transport_header, which is set along with csum_start
  in skb_partial_csum_set in the normal header_ops datapath.

Turns out skbs can arrive in this branch without the transport
header set, e.g., through BPF redirection.

Revise the check back to check csum_start directly, and only if
CHECKSUM_PARTIAL. Do leave the check in the updated location.
Check field regardless of whether TUNNEL_CSUM is configured.

## References
- https://git.kernel.org/stable/c/0c92d813c7c9ca2212ecd879232e7d87362fce98
- https://git.kernel.org/stable/c/0ffa268724656633af5f37a38c212326d98ebe8c
- https://git.kernel.org/stable/c/3d08bc3a5d9b2106f5c8bcf1adb73147824aa006
- https://git.kernel.org/stable/c/7596bd7920985f7fc8579a92e48bc53ce4475b21
- https://git.kernel.org/stable/c/8d21e9963bec1aad2280cdd034c8993033ef2948
- https://git.kernel.org/stable/c/e6b6f98fc7605c06c0a3baa70f62c534d7b4ce58
- https://git.kernel.org/stable/c/fbeb8dfa8b87ef259eef0c89e39b53962a3cf604
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49340.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49340
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
