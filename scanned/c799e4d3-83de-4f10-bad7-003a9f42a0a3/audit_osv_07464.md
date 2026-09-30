# [H] SeaweedFS: Authenticated Cross-Prefix IDOR in Filer TUS Handler Enables Arbitrary Write to Tenant-Forbidden Paths

## Summary
Severity: High
Advisory: BIT-seaweedfs-2026-77368
Aliases: CVE-2026-77368, GHSA-99q7-x53r-6j4g
Ecosystem: Bitnami
Published: 2026-09-02
Source: https://osv.dev/vulnerability/BIT-seaweedfs-2026-77368
Type: osv

## Affected
- Bitnami: `seaweedfs` — affected >=4.39.0 <4.40.0

## Details
SeaweedFS is a distributed storage system for files and blobs. In version 4.39, the filer's TUS resumable-upload handler checks JWT allowed_prefixes scoping only when a session is created, letting a low-privilege tenant hijack another tenant's upload session to write content to filer paths their own token forbids. The HEAD, PATCH, and DELETE verbs that act on an existing session by its id never verify that the session's stored target path falls within the caller's allowed prefixes, so a tenant who obtains another upload's session identifier can PATCH attacker bytes into it and, on completion, have the file land at the victim's out-of-scope path. The same token can also DELETE other tenants' sessions and HEAD them to read upload progress and size, defeating the JWT prefix isolation. This vulnerability only affects deployments that configure filer JWT signing and have TUS uploads enabled. This issue is fixed in version 4.40.

## References
- https://github.com/seaweedfs/seaweedfs/commit/ce82e3a057080162a9fba11889157d2255815f71
- https://github.com/seaweedfs/seaweedfs/commit/fa549e9c83b7799d512157d728f52052912831af
- https://github.com/seaweedfs/seaweedfs/security/advisories/GHSA-99q7-x53r-6j4g
- https://nvd.nist.gov/vuln/detail/CVE-2026-77368
