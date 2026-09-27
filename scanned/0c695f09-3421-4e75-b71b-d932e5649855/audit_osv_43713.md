# [C] veth: fix skb length accounting after XDP frag adjustment

## Summary
Severity: Critical
Advisory: CVE-2026-74612
Ecosystem: Linux
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74612
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.184, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

veth: fix skb length accounting after XDP frag adjustment

veth exposes non-linear skb fragments through an xdp_buff. If an XDP
program adjusts the fragment area, veth_xdp_rcv_skb() copies
xdp_frags_size back to skb->data_len but leaves skb->len containing the
old fragment contribution.

After a fragment shrink, this makes skb_headlen() larger than the actual
linear area. In the reproduced UDP receive path, __skb_datagram_iter()
copied 1024 bytes past the actual linear tail to userspace, starting at
struct skb_shared_info. The copied bytes included the affected skb's
nr_frags, xdp_frags_size, and a kernel pointer from
skb_shinfo(skb)->frags[0]. Real packet data was displaced by the same
amount and truncated at the end.

Subtract the old data_len before replacing it and add the new data_len
afterwards, keeping skb->len and skb->data_len synchronized.

Additionally, bpf_xdp_pull_data() can advance data_end while leaving
frags present. The skb is then still non-linear, so the old
__skb_put(skb, off) triggers SKB_LINEAR_ASSERT().

Use skb_set_tail_pointer() and update skb->len explicitly instead,
following bpf_prog_run_generic_xdp(). Unlike __skb_put(),
skb_set_tail_pointer() does not require a linear skb.

A 60000-byte UDP datagram on a veth pair with MTU 64000 was shortened by
1024 bytes from its fragment area. Before the fix, all 10 runs produced
corrupted payloads. After the fix, all 10 runs matched the expected
payload exactly. A forced-tailroom reproducer also exercises
bpf_xdp_pull_data() with frags still present; the old code triggers
SKB_LINEAR_ASSERT(), while this fix passes 10/10 runs.

## References
- https://git.kernel.org/stable/c/0c3024afabb8064b141f3cedcb1ddd6ab05ad9d5
- https://git.kernel.org/stable/c/2f2a7f3f8b9f1bffc9b0488aa02b6951b2aec139
- https://git.kernel.org/stable/c/3205b0652a37255dbb7ca8f3d942c8d8aa677c21
- https://git.kernel.org/stable/c/41b96667d42b74bb4b137f1bb78b611a953c5943
- https://git.kernel.org/stable/c/cb6379feaaff11c4e1e79c26c745ffa23182768a
- https://git.kernel.org/stable/c/cdf745b7a777f87f51666e5d8f4c6fc279bcf54d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74612.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74612
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
