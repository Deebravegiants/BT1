# [H] SeaweedFS: Filer JWT allowed_prefixes literal prefix match allows cross-tenant access to sibling paths

## Summary
Severity: High
Advisory: BIT-seaweedfs-2026-72921
Aliases: CVE-2026-72921, GHSA-gv5w-hfx8-8cwq, GO-2026-6361
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-seaweedfs-2026-72921
Type: osv

## Affected
- Bitnami: `seaweedfs` — affected >=0 <4.24.0

## Details
SeaweedFS is a distributed storage system. Prior to 4.24, the weed/server/filer_server_handlers.go allowed_prefixes authorization check used strings.HasPrefix on raw path strings, so a filer JWT scoped to /tenant1 also authorized sibling paths such as /tenant1234, /tenant1-old, and /tenant1backup, enabling cross-tenant reads and writes with a valid scoped token. This issue is fixed in version 4.24.

## References
- https://github.com/seaweedfs/seaweedfs/commit/05ed5c9ae8a2a45101b52b61d02f170d20d587ff
- https://github.com/seaweedfs/seaweedfs/pull/9439
- https://github.com/seaweedfs/seaweedfs/releases/tag/4.24
- https://github.com/seaweedfs/seaweedfs/security/advisories/GHSA-gv5w-hfx8-8cwq
- https://nvd.nist.gov/vuln/detail/CVE-2026-72921
