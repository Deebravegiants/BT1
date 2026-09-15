# [C] SeaweedFS: Unauthenticated SSRF with response read-back via VolumeServer.FetchAndWriteNeedle

## Summary
Severity: Critical
Advisory: GHSA-87fv-vqqr-m4jr
CVE: CVE-2026-73080
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-11
Source: https://github.com/advisories/GHSA-87fv-vqqr-m4jr
Type: github-advisory

## Affected
- Go: `github.com/seaweedfs/seaweedfs` — affected >=0 <0.0.0-20260512171120-69da20bdaec9

## Details
### Impact
`VolumeServer.FetchAndWriteNeedle` fetches a caller-supplied remote endpoint and writes the response into a needle. Before 4.24 this RPC performed no authentication and no validation of the target, so anyone able to reach a volume server's gRPC port could coerce the server into issuing requests to arbitrary hosts — including loopback, link-local, RFC 1918, and cloud metadata endpoints such as `169.254.169.254` — and read the response back. On cloud deployments this discloses instance metadata and IAM credentials, and can be used to reach otherwise-unexposed internal services (SSRF with response read-back).

The volume server gRPC plane is unauthenticated on a default deployment, so no credentials are required. Configuring the documented JWT signing keys does not close it, because that hardening does not apply to this RPC.

### Affected component
- `weed/server/volume_grpc_remote.go` (`FetchAndWriteNeedle`)
- `weed/remote_storage/s3/s3_storage_client.go`

### Patches
Fixed in **4.24**. `FetchAndWriteNeedle` now requires admin authorization and refuses loopback / link-local / RFC 1918 / IMDS destinations through a guarded dialer that resolves the host itself and pins the resolved address for the duration of the request, defeating DNS-rebinding. The Rust volume server carries the equivalent endpoint validation.

### Workarounds
Restrict volume server gRPC ports to trusted hosts via firewall / network policy, and enable mTLS via `security.toml`.

## References
- https://github.com/seaweedfs/seaweedfs/security/advisories/GHSA-87fv-vqqr-m4jr
- https://github.com/seaweedfs/seaweedfs/pull/9441
- https://github.com/seaweedfs/seaweedfs/commit/69da20bdaec923e5a43d8aa71bf3c0a2051fc019
- https://github.com/seaweedfs/seaweedfs
- https://github.com/seaweedfs/seaweedfs/releases/tag/4.24
