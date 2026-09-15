# [H] quiche connection ID retirement can trigger an infinite loop

## Summary
Severity: High
Advisory: GHSA-m3hh-f9gh-74c2
CVE: CVE-2025-7054
CWE: CWE-835
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-07
Source: https://github.com/advisories/GHSA-m3hh-f9gh-74c2
Type: github-advisory

## Affected
- crates.io: `quiche` — affected >=0.15.0 <0.24.5

## Details
## Impact

Cloudflare quiche was discovered to be vulnerable to an infinite loop when sending packets containing RETIRE_CONNECTION_ID frames.

QUIC connections possess a set of connection identifiers (IDs); see [Section 5.1 of RFC 9000](https://datatracker.ietf.org/doc/html/rfc9000#section-5.1). Once the QUIC handshake completes, a local endpoint is responsible for issuing and retiring Connection IDs that are used by the remote peer to populate the Destination Connection ID field in packets sent from remote to local. Each Connection ID has a sequence number to ensure synchronization between peers

An unauthenticated remote attacker can exploit this vulnerability by first completing a handshake and then sending a specially-crafted set of frames that trigger a connection ID retirement in the victim. When the victim attempts to send a packet containing RETIRE_CONNECTION_ID frames, [Section 19.16 of RFC 9000](https://datatracker.ietf.org/doc/html/rfc9000#section-19.16) requires that the sequence number of the retired connection ID must not be the same as the sequence number of the connection ID used by the packet. In other words, a packet cannot contain a frame that retires itself.  In scenarios such as path migration, it is possible for there to be multiple active paths with different active connection IDs that could be used to retire each other. The exploit triggered an unintentional behaviour of a quiche design feature that supports retirement across paths while maintaining full connection ID  synchronization, leading to an infinite loop.

## Patches

quiche 0.24.5 is the earliest version containing the fix for the issue

## References
- https://github.com/cloudflare/quiche/security/advisories/GHSA-m3hh-f9gh-74c2
- https://nvd.nist.gov/vuln/detail/CVE-2025-7054
- https://github.com/cloudflare/quiche
