# [C] veth: convert frag_list skbs before running XDP

## Summary
Severity: Critical
Advisory: CVE-2026-74476
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74476
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

veth: convert frag_list skbs before running XDP

A frag_list skb can reach veth with data_len set but nr_frags zero.
veth_convert_skb_to_xdp_buff() only converts skbs that are shared,
locked, have frags[], or do not have enough headroom. It later uses
skb_is_nonlinear() to decide whether to set XDP_FLAGS_HAS_FRAGS and
xdp_frags_size.

That exposes frag_list data to XDP as if it were stored in frags[], but
frags[] is empty. AF_XDP copy mode can then trust the bogus XDP fragment
metadata, walk an empty fragment entry, and crash in memcpy() from
__xsk_rcv().

Route non-linear skbs through skb_pp_cow_data() before exposing them to
XDP, and only advertise XDP frags when the resulting skb has frags[].
skb_copy_bits() already handles frag_list input, and skb_pp_cow_data()
builds frags[] output with skb_add_rx_frag(), which is the
representation XDP multi-buffer expects.

## References
- https://git.kernel.org/stable/c/04958dba44dc795dc79ce2fcbc117821bbbd6542
- https://git.kernel.org/stable/c/0be3632597b8349d43a7dc4244b492dc62a05998
- https://git.kernel.org/stable/c/5c1c15c540fc45820ce3033c319151ec891bc10a
- https://git.kernel.org/stable/c/b24ba0bbffe3e23eb2f6838881c1fabcb29fb9fb
- https://git.kernel.org/stable/c/d0d6415963040c401e7a7e4e482a698ba52448cb
- https://git.kernel.org/stable/c/f9c1fff857e93be709c8b52ed1a643f37bd82c66
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74476.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74476
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
