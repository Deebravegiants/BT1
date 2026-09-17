# [H] Net::BitTorrent versions through 2.1.0 for Perl allow remote memory exhaustion via an uncapped peer-wire message-length prefix

## Summary
Severity: High
Advisory: CVE-2026-57080
Aliases: GHSA-7jr6-2jf4-6qc4
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-57080
Type: osv

## Details
Net::BitTorrent versions through 2.1.0 for Perl allow remote memory exhaustion via an uncapped peer-wire message-length prefix.

The peer-wire framing in _process_messages trusts the 4-byte length prefix sent by a connected peer with no upper bound, while receive_data appends every inbound byte to the input buffer. A peer announces a length prefix of up to about 4 GiB and then streams bytes; the decoder waits until the buffer holds the full message before processing it, so the buffer grows without limit.

Peer connections are unauthenticated, so any peer in the swarm exhausts the downloading process's memory. The largest legitimate message is a 16 KiB piece block, so any announced length far above that is anomalous.

## References
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57080.json
- https://github.com/sanko/Net-BitTorrent.pm/security/advisories/GHSA-7jr6-2jf4-6qc4
- https://metacpan.org/release/SANKO/Net-BitTorrent-v2.1.0/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-57080
- https://github.com/sanko/Net-BitTorrent.pm
