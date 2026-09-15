# [M] Quicly is vulnerable to stateless reset injection

## Summary
Severity: Medium
Advisory: CVE-2026-44434
Aliases: GHSA-899f-49jq-pfh8
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-44434
Type: osv

## Details
Quicly is an IETF QUIC protocol implementation intended primarily for use within the H2O HTTP server. Prior to commit dccf5d4, Quicly was vulnerable to stateless reset injection through lack of packet entry validation. The QUIC protocol is designed to withstand packet injection attacks, once the handshake is complete. Only packets that carry some secret patterns are considered as stateless resets. Quicly allows the peer to share up to 4 such patterns per connection. However, until now, it failed to determine which of the 4 slots that it uses to retain the secret patterns contains a valid entry. As the slots are zero-initialized, the failure meant that, unless the peer advertised 4 of such patterns, an all-zero pattern was treated as a stateless reset.In effect, this allowed an on-path attacker to reset QUIC connections governed by Quicly. This issue has been fixed by commit dccf5d4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44434.json
- https://github.com/h2o/quicly/security/advisories/GHSA-899f-49jq-pfh8
- https://nvd.nist.gov/vuln/detail/CVE-2026-44434
- https://github.com/h2o/quicly/commit/dccf5d4579c7ae9dd6e8f90c36d52e311bb60710
