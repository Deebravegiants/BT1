# [C] netfilter: socket: Lookup orig tuple for IPv6 SNAT

## Summary
Severity: Critical
Advisory: CVE-2025-22021
Ecosystem: Linux
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22021
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <5.4.292, >=5.5.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.133, >=6.2.0 <6.6.86, >=6.7.0 <6.12.22, >=6.13.0 <6.13.10, >=6.14.0 <6.14.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: socket: Lookup orig tuple for IPv6 SNAT

nf_sk_lookup_slow_v4 does the conntrack lookup for IPv4 packets to
restore the original 5-tuple in case of SNAT, to be able to find the
right socket (if any). Then socket_match() can correctly check whether
the socket was transparent.

However, the IPv6 counterpart (nf_sk_lookup_slow_v6) lacks this
conntrack lookup, making xt_socket fail to match on the socket when the
packet was SNATed. Add the same logic to nf_sk_lookup_slow_v6.

IPv6 SNAT is used in Kubernetes clusters for pod-to-world packets, as
pods' addresses are in the fd00::/8 ULA subnet and need to be replaced
with the node's external address. Cilium leverages Envoy to enforce L7
policies, and Envoy uses transparent sockets. Cilium inserts an iptables
prerouting rule that matches on `-m socket --transparent` and redirects
the packets to localhost, but it fails to match SNATed IPv6 packets due
to that missing conntrack lookup.

## References
- https://git.kernel.org/stable/c/1ca2169cc19dca893c7aae6af122852097435d16
- https://git.kernel.org/stable/c/1ec43100f7123010730b7ddfc3d5c2eac19e70e7
- https://git.kernel.org/stable/c/221c27259324ec1404f028d4f5a0f2ae7f63ee23
- https://git.kernel.org/stable/c/2bb139e483f8cbe488d19d8c1135ac3615e2668c
- https://git.kernel.org/stable/c/41904cbb343d115931d6bf79aa2c815cac4ef72b
- https://git.kernel.org/stable/c/5251041573850e5020cd447374e23010be698898
- https://git.kernel.org/stable/c/58ab63d3ded2ca6141357a2b24eee8453d0f871d
- https://git.kernel.org/stable/c/6488b96a79a26e19100ad872622f04e93b638d7f
- https://git.kernel.org/stable/c/932b32ffd7604fb00b5c57e239a3cc4d901ccf6e
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22021.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22021
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
