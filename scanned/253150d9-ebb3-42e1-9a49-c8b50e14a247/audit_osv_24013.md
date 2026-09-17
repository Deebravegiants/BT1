# [H] net: gso: fix panic on frag_list with mixed head alloc types

## Summary
Severity: High
Advisory: CVE-2022-49872
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49872
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.9.334, >=4.10.0 <4.14.300, >=4.15.0 <4.19.267, >=4.20.0 <5.4.225, >=5.3.0 <5.10.155, >=5.5.0 <5.15.79, >=5.11.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: gso: fix panic on frag_list with mixed head alloc types

Since commit 3dcbdb134f32 ("net: gso: Fix skb_segment splat when
splitting gso_size mangled skb having linear-headed frag_list"), it is
allowed to change gso_size of a GRO packet. However, that commit assumes
that "checking the first list_skb member suffices; i.e if either of the
list_skb members have non head_frag head, then the first one has too".

It turns out this assumption does not hold. We've seen BUG_ON being hit
in skb_segment when skbs on the frag_list had differing head_frag with
the vmxnet3 driver. This happens because __netdev_alloc_skb and
__napi_alloc_skb can return a skb that is page backed or kmalloced
depending on the requested size. As the result, the last small skb in
the GRO packet can be kmalloced.

There are three different locations where this can be fixed:

(1) We could check head_frag in GRO and not allow GROing skbs with
    different head_frag. However, that would lead to performance
    regression on normal forward paths with unmodified gso_size, where
    !head_frag in the last packet is not a problem.

(2) Set a flag in bpf_skb_net_grow and bpf_skb_net_shrink indicating
    that NETIF_F_SG is undesirable. That would need to eat a bit in
    sk_buff. Furthermore, that flag can be unset when all skbs on the
    frag_list are page backed. To retain good performance,
    bpf_skb_net_grow/shrink would have to walk the frag_list.

(3) Walk the frag_list in skb_segment when determining whether
    NETIF_F_SG should be cleared. This of course slows things down.

This patch implements (3). To limit the performance impact in
skb_segment, the list is walked only for skbs with SKB_GSO_DODGY set
that have gso_size changed. Normal paths thus will not hit it.

We could check only the last skb but since we need to walk the whole
list anyway, let's stay on the safe side.

## References
- https://git.kernel.org/stable/c/0a9f56e525ea871d3950b90076912f5c7494f00f
- https://git.kernel.org/stable/c/50868de7dc4e7f0fcadd6029f32bf4387c102ee6
- https://git.kernel.org/stable/c/5876b7f249a1ecbbcc8e35072c3828d6526d1c3a
- https://git.kernel.org/stable/c/598d9e30927b15731e83797fbd700ecf399f42dd
- https://git.kernel.org/stable/c/65ad047fd83502447269fda8fd26c99077a9af47
- https://git.kernel.org/stable/c/9e4b7a99a03aefd37ba7bb1f022c8efab5019165
- https://git.kernel.org/stable/c/ad25a115f50800c6847e0d841c5c7992a9f7c1b3
- https://git.kernel.org/stable/c/bd5362e58721e4d0d1a37796593bd6e51536ce7a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49872.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49872
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
