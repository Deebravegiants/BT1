# [C] SeaweedFS: Unauthenticated filer IAM gRPC service grants S3 administrative control

## Summary
Severity: Critical
Advisory: GHSA-2v6v-25fm-p4fg
CVE: CVE-2026-72920
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-2v6v-25fm-p4fg
Type: github-advisory

## Affected
- Go: `github.com/seaweedfs/seaweedfs` — affected >=0 <0.0.0-20260512171108-5e8f99f40a8a

## Details
### Impact
The filer registered the IAM gRPC service (`SeaweedIdentityAccessManagement`) with no authentication. Any client able to reach the filer gRPC port could invoke IAM RPCs — `CreateUser`, `CreateAccessKey`, `PutUserPolicy`, and related calls — to mint credentials and grant itself S3 administrative privileges. This fully compromises the confidentiality, integrity, and availability of stored objects.

No credentials are required, and enabling the documented JWT signing keys does not close it: the IAM gRPC service was not gated by that mechanism. Even under mTLS, the listener-level `allowed_commonNames` ACL applies to the port rather than to individual RPCs, so any cluster mesh certificate could reach these administrative calls.

### Affected component
- `weed/server/filer_server_handlers_iam_grpc.go`
- `weed/command/filer.go`

### Patches
Fixed in **4.24**. Every IAM RPC now requires a Bearer token signed with the filer admin signing key (`jwt.filer_signing.key`), and the service refuses to register when no signing key is configured — removing the unauthenticated default entirely.

### Workarounds
Restrict the filer gRPC port to trusted hosts. Configure `jwt.filer_signing.key` in `security.toml` and upgrade to 4.24; operators that use the IAM RPCs must attach an admin-signed Bearer token on each call.

### References
- Fixed by seaweedfs/seaweedfs#9442 (follow-ups: #9498, #9508, #9514, #9536)
- Reported by Kadir Arslan (https://github.com/KadirArslan)

## References
- https://github.com/seaweedfs/seaweedfs/security/advisories/GHSA-2v6v-25fm-p4fg
- https://nvd.nist.gov/vuln/detail/CVE-2026-72920
- https://github.com/seaweedfs/seaweedfs/pull/9442
- https://github.com/seaweedfs/seaweedfs/commit/5e8f99f40a8abc7b449aefd260516443377041c7
- https://github.com/seaweedfs/seaweedfs
- https://github.com/seaweedfs/seaweedfs/releases/tag/4.24
