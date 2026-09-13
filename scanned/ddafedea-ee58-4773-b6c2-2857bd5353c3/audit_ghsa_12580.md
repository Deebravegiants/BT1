# [H] Incomplete Internal State Distinction in GRPCWebToHTTP2ServerCodec

## Summary
Severity: High
Advisory: GHSA-2jx2-qcm4-rf9h
CVE: CVE-2021-36153
Ecosystem: SwiftURL
Published: 2023-06-09
Source: https://github.com/advisories/GHSA-2jx2-qcm4-rf9h
Type: github-advisory

## Affected
- SwiftURL: `github.com/grpc/grpc-swift` — affected >=0 <1.2.0

## Details
### Impact

Affected gRPC Swift servers are vulnerable to precondition failures when parsing certain gRPC Web requests. This may lead to a denial of service.

### Patches

The problem has been fixed in 1.2.0.

### Workarounds

No workaround is available. Users must upgrade.

## References
- https://github.com/grpc/grpc-swift/security/advisories/GHSA-2jx2-qcm4-rf9h
- https://nvd.nist.gov/vuln/detail/CVE-2021-36153
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=35267
- https://github.com/grpc/grpc-swift
- https://github.com/grpc/grpc-swift/releases
