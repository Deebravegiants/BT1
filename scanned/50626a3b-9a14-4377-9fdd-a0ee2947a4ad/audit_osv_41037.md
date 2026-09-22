# [H] Net::BitTorrent versions through 2.1.0 for Perl allow remote memory exhaustion via deeply nested bencoded input

## Summary
Severity: High
Advisory: CVE-2026-57081
Aliases: GHSA-mv44-v82p-89xv
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-57081
Type: osv

## Details
Net::BitTorrent versions through 2.1.0 for Perl allow remote memory exhaustion via deeply nested bencoded input.

bdecode recurses once per nested list or dictionary level with no depth cap, and each recursive call receives the remaining buffer by value while the list and dictionary branches capture the whole remainder, so every live recursion frame keeps its own copy of the shrinking buffer (O(N^2) bytes for an N-deep input). The decoder runs on every untrusted bencode source: .torrent files, BEP09 metadata fetched from peers, DHT messages, and tracker responses.

A bencoded input of roughly 150,000 nested lists (about 150 KB on the wire) drives multi-gigabyte peak memory, so one short message from any peer, or one crafted .torrent file or magnet link, terminates the client.

## References
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57081.json
- https://github.com/sanko/Net-BitTorrent.pm/security/advisories/GHSA-mv44-v82p-89xv
- https://metacpan.org/release/SANKO/Net-BitTorrent-v2.1.0/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-57081
- https://github.com/sanko/Net-BitTorrent.pm
