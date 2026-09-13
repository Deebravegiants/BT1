# [H] ipv6: validate extension header length before copying to cmsg

## Summary
Severity: High
Advisory: CVE-2026-63920
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63920
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: validate extension header length before copying to cmsg

ip6_datagram_recv_specific_ctl() builds IPV6_{HOPOPTS,DSTOPTS,RTHDR}
cmsgs (and their IPV6_2292* legacy counterparts) by trusting the
on-wire hdrlen byte (ptr[1]) when computing the put_cmsg() length.
The length was validated only at parse time (ipv6_parse_hopopts(),
etc.).  An nftables payload-write expression can rewrite hdrlen after
parsing and before the skb reaches recvmsg; the write itself is
in-bounds but put_cmsg() then reads up to ((hdrlen+1) << 3) = 2040
bytes from an 8-byte header.  nftables is reachable from an
unprivileged user namespace, so this is an unprivileged
slab-out-of-bounds read:

  BUG: KASAN: slab-out-of-bounds in put_cmsg+0x3ac/0x540
   put_cmsg+0x3ac/0x540
   udpv6_recvmsg+0xca0/0x1250
   sock_recvmsg+0xdf/0x190
   ____sys_recvmsg+0x1b1/0x620

Add ipv6_get_exthdr_len() which validates that at least two bytes
are accessible before reading the hdrlen field, then checks the
computed length against skb_tail_pointer(skb), returning 0 on
failure.  Extension headers are kept in the linear skb area by
pskb_may_pull() during input, so skb_tail_pointer() is the correct
bound.

Use ipv6_get_exthdr_len() at all non-AH call sites: the five
standalone cmsg blocks (HbH, 2292HbH, 2292DSTOPTS x2, 2292RTHDR)
and the three standard cases in the extension-header walk loop
(DSTOPTS, ROUTING, default).  AH retains an inline bounds check
because its length formula differs ((ptr[1]+2)<<2).

The walk loop also gets a pre-read bounds check at the top to
validate ptr before any case accesses ptr[0] or ptr[1].

When the walk loop detects a corrupted header, return from the
function instead of continuing to process later socket options.

## References
- https://git.kernel.org/stable/c/08464413e628803bd10cb1df68d0138665f2f885
- https://git.kernel.org/stable/c/0d330eff318c0f44d4fb0ad2c2aef38f87f24c90
- https://git.kernel.org/stable/c/81394827dfb72772c50d0ae3bdfa094428a5d76d
- https://git.kernel.org/stable/c/931b4a1f13408c2507719890f78f7227c34a0282
- https://git.kernel.org/stable/c/a29768d56eb3798c052ad3281b05596e695a17af
- https://git.kernel.org/stable/c/a35daeabb433686234b010ebf7b53778dbd6c9b8
- https://git.kernel.org/stable/c/dd433671fef381fdaf7b530c631e6b782d66e224
- https://git.kernel.org/stable/c/eb18a1b1644e4cad978df2131e2bb9a2e6886992
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63920.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63920
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
