# [M] CVE-2021-47546

## Summary
Severity: Medium
Advisory: CVE-2021-47546
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47546
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: fix memory leak in fib6_rule_suppress

The kernel leaks memory when a `fib` rule is present in IPv6 nftables
firewall rules and a suppress_prefix rule is present in the IPv6 routing
rules (used by certain tools such as wg-quick). In such scenarios, every
incoming packet will leak an allocation in `ip6_dst_cache` slab cache.

After some hours of `bpftrace`-ing and source code reading, I tracked
down the issue to ca7a03c41753 ("ipv6: do not free rt if
FIB_LOOKUP_NOREF is set on suppress rule").

The problem with that change is that the generic `args->flags` always have
`FIB_LOOKUP_NOREF` set[1][2] but the IPv6-specific flag
`RT6_LOOKUP_F_DST_NOREF` might not be, leading to `fib6_rule_suppress` not
decreasing the refcount when needed.

How to reproduce:
 - Add the following nftables rule to a prerouting chain:
     meta nfproto ipv6 fib saddr . mark . iif oif missing drop
   This can be done with:
     sudo nft create table inet test
     sudo nft create chain inet test test_chain '{ type filter hook prerouting priority filter + 10; policy accept; }'
     sudo nft add rule inet test test_chain meta nfproto ipv6 fib saddr . mark . iif oif missing drop
 - Run:
     sudo ip -6 rule add table main suppress_prefixlength 0
 - Watch `sudo slabtop -o | grep ip6_dst_cache` to see memory usage increase
   with every incoming ipv6 packet.

This patch exposes the protocol-specific flags to the protocol
specific `suppress` function, and check the protocol-specific `flags`
argument for RT6_LOOKUP_F_DST_NOREF instead of the generic
FIB_LOOKUP_NOREF when decreasing the refcount, like this.

[1]: https://github.com/torvalds/linux/blob/ca7a03c4175366a92cee0ccc4fec0038c3266e26/net/ipv6/fib6_rules.c#L71
[2]: https://github.com/torvalds/linux/blob/ca7a03c4175366a92cee0ccc4fec0038c3266e26/net/ipv6/fib6_rules.c#L99

## References
- https://git.kernel.org/stable/c/209d35ee34e25f9668c404350a1c86d914c54ffa
- https://git.kernel.org/stable/c/8ef8a76a340ebdb2c2eea3f6fb0ebbed09a16383
- https://git.kernel.org/stable/c/cdef485217d30382f3bf6448c54b4401648fe3f1
- https://git.kernel.org/stable/c/ee38eb8cf9a7323884c2b8e0adbbeb2192d31e29
