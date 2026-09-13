# [H] ipvs: use parsed transport offset in SCTP state lookup

## Summary
Severity: High
Advisory: CVE-2026-72021
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72021
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipvs: use parsed transport offset in SCTP state lookup

set_sctp_state() reads the SCTP chunk header again in order to drive the
IPVS SCTP state table. For IPv6 it computes the offset with
sizeof(struct ipv6hdr), while the surrounding IPVS code uses iph.len from
ip_vs_fill_iph_skb(), where ipv6_find_hdr() has already skipped
extension headers and found the real transport header.

This makes the state machine read from the wrong offset for IPv6 SCTP
packets that carry extension headers. For example, an INIT packet with an
8-byte destination options header can be scheduled correctly by
sctp_conn_schedule(), but set_sctp_state() reads the first byte of the
SCTP verification tag as a DATA chunk type. The connection then moves
from NONE to ESTABLISHED instead of INIT1, gets the longer established
timeout, and updates the active/inactive destination counters
incorrectly. This happens even though the SCTP handshake has not
completed.

Use the parsed transport offset passed down from ip_vs_set_state() for
the SCTP chunk-header lookup. For IPv4 and IPv6 packets without
extension headers this preserves the existing offset.

## References
- https://git.kernel.org/stable/c/247d055504dcc852e539b9f7f30d19f9741474bf
- https://git.kernel.org/stable/c/290e9e8389b556efc603522e28bd1543846aa336
- https://git.kernel.org/stable/c/2f75c0faa3361b28e36cc0512b3299e163e25789
- https://git.kernel.org/stable/c/9cb5ac594ca76d3a71803b23b74c835b0721e628
- https://git.kernel.org/stable/c/9f94573ab962a9e81954b755da016fa3cd2f5039
- https://git.kernel.org/stable/c/a4a2d2e483d79cc2ad3a170674cf159644acf22b
- https://git.kernel.org/stable/c/d2b8b1557ec07ea1bb5dddbceaf4dfe63d388e27
- https://git.kernel.org/stable/c/e5d0bb8871668f20de8f3c94b5ae3f372346bc6e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72021.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72021
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
