# [M] Uncontrolled Recursion in HTTP2ToRawGRPCServerCodec

## Summary
Severity: Medium
Advisory: GHSA-4rhq-vq24-88gw
CVE: CVE-2021-36154
CWE: CWE-674
Ecosystem: SwiftURL
Published: 2023-05-22
Source: https://github.com/advisories/GHSA-4rhq-vq24-88gw
Type: github-advisory

## Affected
- SwiftURL: `github.com/grpc/grpc-swift` — affected >=0 <1.2.0

## Details
### Impact

Affected gRPC Swift servers are vulnerable to uncontrolled recursion and stack consumption when parsing certain payloads. This may lead to a denial of service.

### Patches

The problem has been fixed in 1.2.0.

### Workarounds

No workaround is available. Users must upgrade.

## References
- https://github.com/grpc/grpc-swift/security/advisories/GHSA-4rhq-vq24-88gw
- https://nvd.nist.gov/vuln/detail/CVE-2021-36154
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=35274
- https://github.com/grpc/grpc-swift
- https://github.com/grpc/grpc-swift/releases/tag/1.2.0
