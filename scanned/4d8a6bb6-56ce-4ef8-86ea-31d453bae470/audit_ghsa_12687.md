# [H] Uncontrolled Resource Consumption in LengthPrefixedMessageReader

## Summary
Severity: High
Advisory: GHSA-rxmj-hg9v-vp3p
CVE: CVE-2021-36155
CWE: CWE-120, CWE-770
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-09
Source: https://github.com/advisories/GHSA-rxmj-hg9v-vp3p
Type: github-advisory

## Affected
- SwiftURL: `github.com/grpc/grpc-swift` — affected >=0 <1.2.0

## Details
### Impact

Affected gRPC Swift clients and servers are vulnerable to uncontrolled resource consumption attacks. Excessive memory may be allocated when parsing messages. This can lead to a denial of service.

### Patches

The problem has been fixed in 1.2.0.

### Workarounds

No workaround is available. Users must upgrade.

## References
- https://github.com/grpc/grpc-swift/security/advisories/GHSA-rxmj-hg9v-vp3p
- https://nvd.nist.gov/vuln/detail/CVE-2021-36155
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=35303
- https://github.com/grpc/grpc-swift
- https://github.com/grpc/grpc-swift/releases/tag/1.2.0
