# [C] amt: re-read skb header pointers after every pull

## Summary
Severity: Critical
Advisory: CVE-2026-68302
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68302
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

amt: re-read skb header pointers after every pull

Several AMT receive and transmit paths cache a pointer into the skb head
(ip_hdr(), ipv6_hdr(), eth_hdr() or the AMT message header) and then call
a helper that can reallocate that head before the cached pointer is used
again.  pskb_may_pull(), ip_mc_may_pull(), ipv6_mc_may_pull(),
iptunnel_pull_header(), ip_mc_check_igmp() and ipv6_mc_check_mld() can all
free the old head and move the data, so a pointer taken before the call
dangles afterwards and the later access is a use-after-free of the freed
head.

The affected sites are:

  amt_rcv() caches ip_hdr() before amt_parse_type() pulls, then reads
  iph->saddr.

  amt_dev_xmit() caches ip_hdr()/ipv6_hdr() before ip_mc_check_igmp()/
  ipv6_mc_check_mld() and pskb_may_pull(), then reads the group address.

  amt_multicast_data_handler() caches eth_hdr() before pskb_may_pull(),
  then writes the L2 header.

  amt_membership_query_handler() caches the AMT header, the outer and
  inner eth_hdr() and ip_hdr() before iptunnel_pull_header() and several
  pulls, then reads and writes them.

  amt_igmpv3_report_handler() and amt_mldv2_report_handler() cache
  ip_hdr()/ipv6_hdr() and the current group record and read the record
  count from the report header inside the record loop, across the
  *_mc_may_pull() calls.

  amt_update_handler() caches ip_hdr() and the AMT membership-update
  header before pskb_may_pull(), iptunnel_pull_header(),
  ip_mc_check_igmp() and the report handler, then reads iph->daddr and
  amtmu->nonce / amtmu->response_mac.

Fix each site by either snapshotting the scalar that is used after the
pull before the first pull runs, or re-deriving the header pointer from
the skb after the last pull that can move the head.  Values that are
stable across the pull (source and group address, the response MAC and
nonce, the record count, the outer source MAC) are snapshotted; pointers
that are written through or read repeatedly are re-derived.

## References
- https://git.kernel.org/stable/c/3656a79f94c471827a08f2cacce5f94ad5e52c24
- https://git.kernel.org/stable/c/37ff890f9c18dfbcf57e17199901d4fd1e4c174e
- https://git.kernel.org/stable/c/7746d588d42a4ac0117b68ed8e9b22a9da53dfb7
- https://git.kernel.org/stable/c/7f48e3ddad8e97545b25788b8203b3a539df1621
- https://git.kernel.org/stable/c/9005b221cb1f9c3c1a2ef656fb0e8fa80c0a187e
- https://git.kernel.org/stable/c/ca0e8b661957f777591efe874cd9d9a63619cd99
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68302.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68302
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
