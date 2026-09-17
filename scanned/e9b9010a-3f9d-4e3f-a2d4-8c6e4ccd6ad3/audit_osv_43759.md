# [H] netfilter: nf_flow_table: drop existing skb dst before skb_dst_set_noref()

## Summary
Severity: High
Advisory: CVE-2026-74695
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74695
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_flow_table: drop existing skb dst before skb_dst_set_noref()

Incoming skbs passing through netfilter flowtable offload hooks (or XFRM
offload path) might already carry a ref-counted dst_entry assigned during
earlier RX or routing steps.

Calling skb_dst_set_noref() when skb already holds a ref-counted dst
overwrites skb->_skb_refdst, leaking the previous dst_entry reference
count and triggering a DEBUG_NET_WARN_ON_ONCE assertion in
skb_dst_check_unset():

  WARNING: at skb_dst_check_unset include/linux/skbuff.h:1170
  WARNING: at skb_dst_set_noref include/linux/skbuff.h:1234
  WARNING: at nf_flow_offload_ip_hook+0xf6c/0x2b60 net/netfilter/nf_flow_table_ip.c:864

Drop any existing dst_entry reference with skb_dst_drop(skb) before
setting the non-referenced flowtable destination.

## References
- https://git.kernel.org/stable/c/12afa450a6a6c0cce2c42b7545a9958f62d8a00c
- https://git.kernel.org/stable/c/538e67e8c7889cf5f93951f5309d1bcb41f86036
- https://git.kernel.org/stable/c/8aecf0bbcc72605592134c917c222207d8f63ab0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74695.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74695
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
