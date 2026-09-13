# [H] netfilter: nft_objref: validate objref and objrefmap expressions

## Summary
Severity: High
Advisory: CVE-2025-40206
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40206
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <6.1.184, >=6.2.0 <6.6.113, >=6.7.0 <6.12.54, >=6.13.0 <6.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_objref: validate objref and objrefmap expressions

Referencing a synproxy stateful object from OUTPUT hook causes kernel
crash due to infinite recursive calls:

BUG: TASK stack guard page was hit at 000000008bda5b8c (stack is 000000003ab1c4a5..00000000494d8b12)
[...]
Call Trace:
 __find_rr_leaf+0x99/0x230
 fib6_table_lookup+0x13b/0x2d0
 ip6_pol_route+0xa4/0x400
 fib6_rule_lookup+0x156/0x240
 ip6_route_output_flags+0xc6/0x150
 __nf_ip6_route+0x23/0x50
 synproxy_send_tcp_ipv6+0x106/0x200
 synproxy_send_client_synack_ipv6+0x1aa/0x1f0
 nft_synproxy_do_eval+0x263/0x310
 nft_do_chain+0x5a8/0x5f0 [nf_tables
 nft_do_chain_inet+0x98/0x110
 nf_hook_slow+0x43/0xc0
 __ip6_local_out+0xf0/0x170
 ip6_local_out+0x17/0x70
 synproxy_send_tcp_ipv6+0x1a2/0x200
 synproxy_send_client_synack_ipv6+0x1aa/0x1f0
[...]

Implement objref and objrefmap expression validate functions.

Currently, only NFT_OBJECT_SYNPROXY object type requires validation.
This will also handle a jump to a chain using a synproxy object from the
OUTPUT hook.

Now when trying to reference a synproxy object in the OUTPUT hook, nft
will produce the following error:

synproxy_crash.nft: Error: Could not process rule: Operation not supported
  synproxy name mysynproxy
  ^^^^^^^^^^^^^^^^^^^^^^^^

## References
- https://git.kernel.org/stable/c/0028e0134c64d9ed21728341a74fcfc59cd0f944
- https://git.kernel.org/stable/c/4c1cf72ec10be5a9ad264650cadffa1fbce6fabd
- https://git.kernel.org/stable/c/7ea55a44493a5a36c3b3293b88bbe4841f9dbaf0
- https://git.kernel.org/stable/c/f31bcea12222a26d6f151df9c4a6d21f2eec1724
- https://git.kernel.org/stable/c/f359b809d54c6e3dd1d039b97e0b68390b0e53e4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40206.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40206
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
