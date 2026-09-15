# [H] Denial of Service via reachable assertion in grpc-swift

## Summary
Severity: High
Advisory: CVE-2022-24777
Aliases: GHSA-r6ww-5963-7r95
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-03-25
Source: https://osv.dev/vulnerability/CVE-2022-24777
Type: osv

## Details
grpc-swift is the Swift language implementation of gRPC, a remote procedure call (RPC) framework. Prior to version 1.7.2, a grpc-swift server is vulnerable to a denial of service attack via a reachable assertion. This is due to incorrect logic when handling GOAWAY frames. The attack is low-effort: it takes very little resources to construct and send the required sequence of frames. The impact on availability is high as the server will crash, dropping all in flight connections and requests. This issue is fixed in version 1.7.2. There are currently no known workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24777.json
- https://github.com/grpc/grpc-swift/security/advisories/GHSA-r6ww-5963-7r95
- https://nvd.nist.gov/vuln/detail/CVE-2022-24777
- https://github.com/grpc/grpc-swift/commit/858f977f2a51fca2292f384cf7a108dc2e73a3bd
