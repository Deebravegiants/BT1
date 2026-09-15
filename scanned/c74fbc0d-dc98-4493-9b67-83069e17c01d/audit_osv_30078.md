# [H] gso: fix udp gso fraglist segmentation after pull from frag_list

## Summary
Severity: High
Advisory: CVE-2024-49978
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49978
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

gso: fix udp gso fraglist segmentation after pull from frag_list

Detect gso fraglist skbs with corrupted geometry (see below) and
pass these to skb_segment instead of skb_segment_list, as the first
can segment them correctly.

Valid SKB_GSO_FRAGLIST skbs
- consist of two or more segments
- the head_skb holds the protocol headers plus first gso_size
- one or more frag_list skbs hold exactly one segment
- all but the last must be gso_size

Optional datapath hooks such as NAT and BPF (bpf_skb_pull_data) can
modify these skbs, breaking these invariants.

In extreme cases they pull all data into skb linear. For UDP, this
causes a NULL ptr deref in __udpv4_gso_segment_list_csum at
udp_hdr(seg->next)->dest.

Detect invalid geometry due to pull, by checking head_skb size.
Don't just drop, as this may blackhole a destination. Convert to be
able to pass to regular skb_segment.

## References
- https://git.kernel.org/stable/c/080e6c9a3908de193a48f646c5ce1bfb15676ffc
- https://git.kernel.org/stable/c/33e28acf42ee863f332a958bfc2f1a284a3659df
- https://git.kernel.org/stable/c/3cd00d2e3655fad3bda96dc1ebf17b6495f86fea
- https://git.kernel.org/stable/c/a1e40ac5b5e9077fe1f7ae0eb88034db0f9ae1ab
- https://git.kernel.org/stable/c/af3122f5fdc0d00581d6e598a668df6bf54c9daa
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49978.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49978
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
