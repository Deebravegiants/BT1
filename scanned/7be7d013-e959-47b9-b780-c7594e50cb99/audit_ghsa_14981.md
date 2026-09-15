# [H] go-grpc-compression has a zstd decompression bombing vulnerability

## Summary
Severity: High
Advisory: GHSA-87m9-rv8p-rgmg
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-06-10
Source: https://github.com/advisories/GHSA-87m9-rv8p-rgmg
Type: github-advisory

## Affected
- Go: `github.com/mostynb/go-grpc-compression` — affected >=1.1.4 <1.2.3

## Details
### Impact

A malicious user could cause a denial of service (DoS) when using a specially crafted gRPC request. The decompression mechanism for zstd did not respect the limits imposed by gRPC, allowing rapid memory usage increases.

Versions v1.1.4 through to v1.2.2 made use of the Decoder.DecodeAll function in github.com/klauspost/compress/zstd to decompress data provided by the peer. The vulnerability is exploitable only by attackers who can send gRPC payloads to users of github.com/mostynb/go-grpc-compression/zstd or github.com/mostynb/go-grpc-compression/nonclobbering/zstd.

### Patches

Version v1.2.3  of github.com/mostynb/go-grpc-compression avoids the issue by not using the Decoder.DecodeAll function in github.com/klauspost/compress/zstd.

All users of github.com/mostynb/go-grpc-compression/zstd or github.com/mostynb/go-grpc-compression/nonclobbering/zstd in the affected versions should update to v1.2.3.

### Workarounds

Other compression formats were not affected, users may consider switching from zstd to another format without upgrading to a newer release.

### References

This issue was uncovered during a security audit performed by [Miroslav Stampar](https://github.com/stamparm/) of [7ASecurity](https://7asecurity.com/), facilitated by [OSTIF](https://ostif.org/), for the OpenTelemetry project.

https://opentelemetry.io/blog/2024/cve-2024-36129
https://github.com/open-telemetry/opentelemetry-collector/security/advisories/GHSA-c74f-6mfw-mm4v

## References
- https://github.com/mostynb/go-grpc-compression/security/advisories/GHSA-87m9-rv8p-rgmg
- https://github.com/mostynb/go-grpc-compression/commit/629c44d3acb9624993cc7de629f47d72109e2ce5
- https://github.com/mostynb/go-grpc-compression
- https://pkg.go.dev/vuln/GO-2024-2911
