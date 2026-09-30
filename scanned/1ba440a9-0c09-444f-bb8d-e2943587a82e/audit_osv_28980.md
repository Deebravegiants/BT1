# [C] net: openvswitch: fix overwriting ct original tuple for ICMPv6

## Summary
Severity: Critical
Advisory: CVE-2024-38558
Ecosystem: Linux
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38558
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <4.19.316, >=4.20.0 <5.4.278, >=5.5.0 <5.10.219, >=5.11.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: openvswitch: fix overwriting ct original tuple for ICMPv6

OVS_PACKET_CMD_EXECUTE has 3 main attributes:
 - OVS_PACKET_ATTR_KEY - Packet metadata in a netlink format.
 - OVS_PACKET_ATTR_PACKET - Binary packet content.
 - OVS_PACKET_ATTR_ACTIONS - Actions to execute on the packet.

OVS_PACKET_ATTR_KEY is parsed first to populate sw_flow_key structure
with the metadata like conntrack state, input port, recirculation id,
etc.  Then the packet itself gets parsed to populate the rest of the
keys from the packet headers.

Whenever the packet parsing code starts parsing the ICMPv6 header, it
first zeroes out fields in the key corresponding to Neighbor Discovery
information even if it is not an ND packet.

It is an 'ipv6.nd' field.  However, the 'ipv6' is a union that shares
the space between 'nd' and 'ct_orig' that holds the original tuple
conntrack metadata parsed from the OVS_PACKET_ATTR_KEY.

ND packets should not normally have conntrack state, so it's fine to
share the space, but normal ICMPv6 Echo packets or maybe other types of
ICMPv6 can have the state attached and it should not be overwritten.

The issue results in all but the last 4 bytes of the destination
address being wiped from the original conntrack tuple leading to
incorrect packet matching and potentially executing wrong actions
in case this packet recirculates within the datapath or goes back
to userspace.

ND fields should not be accessed in non-ND packets, so not clearing
them should be fine.  Executing memset() only for actual ND packets to
avoid the issue.

Initializing the whole thing before parsing is needed because ND packet
may not contain all the options.

The issue only affects the OVS_PACKET_CMD_EXECUTE path and doesn't
affect packets entering OVS datapath from network interfaces, because
in this case CT metadata is populated from skb after the packet is
already parsed.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/0b532f59437f688563e9c58bdc1436fefa46e3b5
- https://git.kernel.org/stable/c/431e9215576d7b728f3f53a704d237a520092120
- https://git.kernel.org/stable/c/483eb70f441e2df66ade78aa7217e6e4caadfef3
- https://git.kernel.org/stable/c/5ab6aecbede080b44b8e34720ab72050bf1e6982
- https://git.kernel.org/stable/c/6a51ac92bf35d34b4996d6eb67e2fe469f573b11
- https://git.kernel.org/stable/c/78741b4caae1e880368cb2f5110635f3ce45ecfd
- https://git.kernel.org/stable/c/7c988176b6c16c516474f6fceebe0f055af5eb56
- https://git.kernel.org/stable/c/9ec8b0ccadb908d92f7ee211a4eff05fd932f3f6
- https://git.kernel.org/stable/c/d73fb8bddf89503c9fae7c42e50d44c89909aad6
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38558.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38558
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
