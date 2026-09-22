# [M] Net::BitTorrent versions before 2.1.0 for Perl generate the MSE Diffie-Hellman private key with a non-cryptographic PRNG

## Summary
Severity: Medium
Advisory: CVE-2026-57082
Aliases: GHSA-g444-x2c5-94hc
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-57082
Type: osv

## Details
Net::BitTorrent versions before 2.1.0 for Perl generate the MSE Diffie-Hellman private key with a non-cryptographic PRNG.

The MSE (Message Stream Encryption) handshake derives its 160-bit Diffie-Hellman private key from Perl's rand(), a non-cryptographic drand48-class generator seeded once per process, in KeyExchange.pm. The shared secret and the RC4 keys derived from it (the SHA-1 of "keyA" or "keyB", the shared secret, and the infohash) therefore depend entirely on a predictable PRNG. The same handshake sends, in cleartext, random padding drawn from the same rand() sequence in _random_pad, immediately after the public key and the private-key draw.

A passive observer of the handshake recovers the PRNG state from the cleartext padding, reconstructs the private key, computes the shared secret from the peer's public key on the wire, derives the RC4 keys, and decrypts the connection, defeating the passive-observation obfuscation MSE provides.

## References
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57082.json
- https://github.com/sanko/Net-BitTorrent.pm/security/advisories/GHSA-g444-x2c5-94hc
- https://metacpan.org/release/SANKO/Net-BitTorrent-v2.1.0/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-57082
- https://github.com/sanko/Net-BitTorrent.pm
