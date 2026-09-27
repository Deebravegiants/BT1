# [H] net: add pskb_may_pull() to skb_gro_receive_list()

## Summary
Severity: High
Advisory: CVE-2026-53235
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53235
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: add pskb_may_pull() to skb_gro_receive_list()

skb_gro_receive_list() calls skb_pull(skb, skb_gro_offset(skb)) without
first ensuring the data is in the linear area via pskb_may_pull(). When
the skb arrives via napi_gro_frags(), skb_headlen can be 0 (all data in
page fragments) while skb_gro_offset is non-zero (after IP+TCP header
parsing). The skb_pull() then decrements skb->len by skb_gro_offset
but skb->data_len stays unchanged, hitting BUG_ON(skb->len < skb->data_len)
in __skb_pull().

The UDP fraglist GRO path already contains this guard at
udp_offload.c:749. Adding it to skb_gro_receive_list() itself provides
centralized protection for all callers (TCP, UDP, and any future
protocols), and ensures the precondition of skb_pull() is satisfied
before it is called.

On pskb_may_pull() failure, set NAPI_GRO_CB(skb)->flush = 1 so the
skb is not held as a new GRO head and is instead delivered through the
normal receive path, matching the UDP handling.

## References
- https://git.kernel.org/stable/c/0cde3a004119db637b401c54e77536e4145fc0b4
- https://git.kernel.org/stable/c/848571dcbbbea7ba44dd4f7ebe1fbb274afe08ac
- https://git.kernel.org/stable/c/9e636c995b7beeb74ea882968248752821c244c4
- https://git.kernel.org/stable/c/f2bb3434544454099a5b6dec213567267b05d79d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53235.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53235
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
