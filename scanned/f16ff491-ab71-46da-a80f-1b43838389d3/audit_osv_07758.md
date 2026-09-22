# [H] Valkey: TLS pending-data processing use-after-free may allow remote code execution

## Summary
Severity: High
Advisory: BIT-valkey-2026-56684
Aliases: CVE-2026-56684, GHSA-53mc-f3m3-99vh
Ecosystem: Bitnami
Published: 2026-08-24
Source: https://osv.dev/vulnerability/BIT-valkey-2026-56684
Type: osv

## Affected
- Bitnami: `valkey` — affected >=9.1.0 <9.1.1

## Details
Valkey is a distributed key-value database. Prior to 7.2.14, 8.0.10, 8.1.9, 9.0.5, and 9.1.1, Valkey's tlsProcessPendingData function iterates pending_list while an authenticated client can trigger CLIENT KILL, causing connTLSClose to delete the iterator's cached next node and producing a use-after-free that can crash the server or potentially allow remote code execution when TLS is enabled. This issue is fixed in versions 7.2.14, 8.0.10, 8.1.9, 9.0.5, and 9.1.1.

## References
- https://github.com/valkey-io/valkey/commit/7cd5bcb7575d750ec2de618db80da58680a10fe3
- https://github.com/valkey-io/valkey/pull/4234
- https://github.com/valkey-io/valkey/releases/tag/7.2.14
- https://github.com/valkey-io/valkey/releases/tag/8.0.10
- https://github.com/valkey-io/valkey/releases/tag/8.1.9
- https://github.com/valkey-io/valkey/releases/tag/9.0.5
- https://github.com/valkey-io/valkey/releases/tag/9.1.1
- https://github.com/valkey-io/valkey/security/advisories/GHSA-53mc-f3m3-99vh
- https://nvd.nist.gov/vuln/detail/CVE-2026-56684
