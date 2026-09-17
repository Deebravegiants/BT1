# [C] netfilter: flowtable: fix and simplify IP6IP6 tunnel handling

## Summary
Severity: Critical
Advisory: CVE-2026-72442
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72442
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: flowtable: fix and simplify IP6IP6 tunnel handling

Fix nf_flow_ip6_tunnel_proto() to use pskb_may_pull() instead of
skb_header_pointer() to ensure the outer IPv6 header is in the skb
headroom, which is required for subsequent packet processing. Move
ctx->offset update inside the IPPROTO_IPV6 conditional block since it
should only be adjusted when an IP6IP6 tunnel is actually detected.
Simplify the rx path by removing ipv6_skip_exthdr() and checking
ip6h->nexthdr directly, as the flowtable fast path only handles simple
IP6IP6 encapsulation without extension headers.
Drop the tunnel encapsulation limit destination option support from the
tx path to match, since the rx path no longer handles extension headers.
Remove the encap_limit parameter from nf_flow_offload_ipv6_forward(),
nf_flow_tunnel_ip6ip6_push() and nf_flow_tunnel_v6_push(), along with
the ipv6_tel_txoption struct and related headroom/MTU adjustments.

## References
- https://git.kernel.org/stable/c/7f8d816a9aa2729d270418f00c9ef5e85bfc1b31
- https://git.kernel.org/stable/c/f4c2d8668d85ed125985da663c824a9c25498257
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72442.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72442
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
