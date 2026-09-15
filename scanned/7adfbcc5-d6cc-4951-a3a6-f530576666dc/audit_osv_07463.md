# [H] SeaweedFS: SFTP path ACL literal prefix match permits cross-tenant file read and overwrite

## Summary
Severity: High
Advisory: BIT-seaweedfs-2026-77317
Aliases: CVE-2026-77317, GHSA-fvpg-g364-j8vh
Ecosystem: Bitnami
Published: 2026-09-02
Source: https://osv.dev/vulnerability/BIT-seaweedfs-2026-77317
Type: osv

## Affected
- Bitnami: `seaweedfs` — affected >=3.88.0 <4.40.0

## Details
SeaweedFS is a distributed storage system for files and blobs. In versions from 3.88 through 4.39, the SFTP server evaluates configured path permissions with a literal string-prefix comparison, so a user scoped to a path is also granted the same access to any sibling path whose name merely begins with the same characters. A user granted access to /tenants/alice therefore also matches /tenants/alice-archive, /tenants/alice2, and similar siblings, because the check does not require a path-component boundary. An authenticated low-privilege SFTP user with a root home directory and narrow path permissions can thereby cross the configured ACL boundary to read another tenant's files, and to overwrite them if granted write, all through the documented SFTP service with its own valid credentials. This issue is fixed in version 4.40.

## References
- https://github.com/seaweedfs/seaweedfs/commit/29981f8d24a62e9571962c4534fb23c48c00bae2
- https://github.com/seaweedfs/seaweedfs/security/advisories/GHSA-fvpg-g364-j8vh
- https://nvd.nist.gov/vuln/detail/CVE-2026-77317
