# [H] Vulnerability in RPKI manifest validation

## Summary
Severity: High
Advisory: GHSA-q76j-58cx-wp5v
CWE: CWE-20
Ecosystem: Maven
Published: 2020-11-13
Source: https://github.com/advisories/GHSA-q76j-58cx-wp5v
Type: github-advisory

## Affected
- Maven: `net.ripe.rpki:rpki-validator-3` — affected >=0 <3.2-2020.10.28.23.06

## Details
A vulnerability in RPKI manifest validation exists when objects on the manifest are hidden, or expired objects are replayed. An attacker successfully exploiting this vulnerability could prevent new ROAs from being received or selectively hide ROAs, causing routes to become INVALID.

To exploit this vulnerability, an attacker would need to perform a man in the middle attack on the TLS connection between the validator and an RRDP repository or perform a man in the middle attack against a rsync-only repository.

The update addresses the vulnerability by implementing validation methods from [RFC 6486bis](https://datatracker.ietf.org/doc/draft-ietf-sidrops-6486bis/00/) and enabling strict validation by default.

## References
- https://github.com/RIPE-NCC/rpki-validator-3/security/advisories/GHSA-q76j-58cx-wp5v
