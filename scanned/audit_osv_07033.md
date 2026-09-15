# [H] Unathenticated connection can hold Bolt channel open

## Summary
Severity: High
Advisory: BIT-neo4j-2026-14587
Aliases: BIT-neo4j-enterprise-2026-14587, CVE-2026-14587
Ecosystem: Bitnami
Published: 2026-08-21
Source: https://osv.dev/vulnerability/BIT-neo4j-2026-14587
Type: osv

## Affected
- Bitnami: `neo4j` — affected >=2025.1.0 <2026.7.0

## Details
Neo4j's Bolt modern handshake decoder treats an overlong capability bit mask the same way it treats a truncated bit mask. When an unauthenticated client sends a selected protocol version followed by 32 continuation bytes in the capability mask, the decoder resets the reader index and waits for more bytes instead of rejecting the protocol message and closing the channel.



Because the same unread bytes remain at the front of the decoder buffer, appending a terminating byte later does not recover the connection. The decoder re-reads the same first 32 continuation bytes, returns without producing a handshake-finalization message, and leaves the channel open.



This can be triggered before authentication by any client that can reach the Bolt connector.

## References
- https://neo4j.com/security/CVE-2026-14587
- https://nvd.nist.gov/vuln/detail/CVE-2026-14587
