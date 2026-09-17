# [C] ipv6: rpl: reserve mac_len headroom when recompressed SRH grows

## Summary
Severity: Critical
Advisory: CVE-2026-43501
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-21
Source: https://osv.dev/vulnerability/CVE-2026-43501
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: rpl: reserve mac_len headroom when recompressed SRH grows

ipv6_rpl_srh_rcv() decompresses an RFC 6554 Source Routing Header, swaps
the next segment into ipv6_hdr->daddr, recompresses, then pulls the old
header and pushes the new one plus the IPv6 header back.  The
recompressed header can be larger than the received one when the swap
reduces the common-prefix length the segments share with daddr (CmprI=0,
CmprE>0, seg[0][0] != daddr[0] gives the maximum +8 bytes).

pskb_expand_head() was gated on segments_left == 0, so on earlier
segments the push consumed unchecked headroom.  Once skb_push() leaves
fewer than skb->mac_len bytes in front of data,
skb_mac_header_rebuild()'s call to:

	skb_set_mac_header(skb, -skb->mac_len);

will store (data - head) - mac_len into the u16 mac_header field, which
wraps to ~65530, and the following memmove() writes mac_len bytes ~64KiB
past skb->head.

A single AF_INET6/SOCK_RAW/IPV6_HDRINCL packet over lo with a two
segment type-3 SRH (CmprI=0, CmprE=15) reaches headroom 8 after one
pass; KASAN reports a 14-byte OOB write in ipv6_rthdr_rcv.

Fix this by expanding the head whenever the remaining room is less than
the push size plus mac_len, and request that much extra so the rebuilt
MAC header fits afterwards.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/0a9e8053f1f8a8e1bfc1dd61ffe67be6c1180402
- https://git.kernel.org/stable/c/4babc2d9fda2df43823b85d08a0180b68f1b0854
- https://git.kernel.org/stable/c/7398ebefbfd4f8a31d4f665a4213302fa995494b
- https://git.kernel.org/stable/c/8e8be63465a5e80394c70324603dfea1bfdad48f
- https://git.kernel.org/stable/c/9e6bf146b55999a095bb14f73a843942456d1adc
- https://git.kernel.org/stable/c/bde199c72d319a4e207f88daabc888317504e2fb
- https://git.kernel.org/stable/c/be1fa0aa9b4fdd5a8b7a61ba520a690a68391e6e
- https://git.kernel.org/stable/c/c261d07a80576dc8ccf394ef8f074f8c67a06b37
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-43501.json
- https://access.redhat.com/errata/RHSA-2026:25191
- https://access.redhat.com/errata/RHSA-2026:25217
- https://access.redhat.com/errata/RHSA-2026:27713
- https://access.redhat.com/errata/RHSA-2026:27731
- https://access.redhat.com/errata/RHSA-2026:33900
- https://access.redhat.com/errata/RHSA-2026:34094
- https://access.redhat.com/errata/RHSA-2026:34095
- https://access.redhat.com/security/cve/CVE-2026-43501
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43501.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43501
