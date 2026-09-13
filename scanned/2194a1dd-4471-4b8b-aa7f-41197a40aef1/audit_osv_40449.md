# [C] ipv6: sit: reload inner IPv6 header after GSO offloads

## Summary
Severity: Critical
Advisory: CVE-2026-53228
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53228
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: sit: reload inner IPv6 header after GSO offloads

ipip6_tunnel_xmit() caches the inner IPv6 header pointer at function
entry and continues using it after iptunnel_handle_offloads().

For GSO skbs, iptunnel_handle_offloads() calls skb_header_unclone().
When the skb header is cloned, skb_header_unclone() can call
pskb_expand_head(), which may move the skb head. The pskb_expand_head()
contract requires pointers into the skb header to be reloaded after the
call.

If the later skb_realloc_headroom() branch is not taken, SIT uses the
stale iph6 pointer to read the inner hop limit and DS field. That can
read from a freed skb head after the old head's remaining clone is
released.

Reload iph6 after the offload helper succeeds and before subsequent
reads from the inner IPv6 header. Keep the existing reload after
skb_realloc_headroom(), since that branch can also replace the skb.

## References
- https://git.kernel.org/stable/c/0bfa7bba1f41aaf5f0604dc712bb4701493e3aa0
- https://git.kernel.org/stable/c/1132e5edc2866c3530be17622153a597095f0e43
- https://git.kernel.org/stable/c/2fa49b2715e1bad12ce3b0fa64e234d9582c8193
- https://git.kernel.org/stable/c/59f80c919713250fe5d25a4d9aea4e49580fa1d4
- https://git.kernel.org/stable/c/9c67b44edb3598d234efae6e44649eb993c03da5
- https://git.kernel.org/stable/c/cb658c2f5f7977c2a1c77c9f239f4bc8196edb5c
- https://git.kernel.org/stable/c/f0e42f0c4337b1f220de1ddd63f47197c7dee4de
- https://git.kernel.org/stable/c/fddd41445a0537b093e6b3f6232c9933cad1e48b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53228.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53228
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
