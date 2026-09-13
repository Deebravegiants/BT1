# [H] gRPC-Go HTTP/2 Rapid Reset vulnerability

## Summary
Severity: High
Advisory: GHSA-m425-mq94-257g
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-25
Source: https://github.com/advisories/GHSA-m425-mq94-257g
Type: github-advisory

## Affected
- Go: `google.golang.org/grpc` — affected >=0 <1.56.3
- Go: `google.golang.org/grpc` — affected >=1.57.0 <1.57.1
- Go: `google.golang.org/grpc` — affected >=1.58.0 <1.58.3

## Details
### Impact
In affected releases of gRPC-Go, it is possible for an attacker to send HTTP/2 requests, cancel them, and send subsequent requests, which is valid by the HTTP/2 protocol, but would cause the gRPC-Go server to launch more concurrent method handlers than the configured maximum stream limit.

### Patches
This vulnerability was addressed by #6703 and has been included in patch releases: 1.56.3, 1.57.1, 1.58.3.  It is also included in the latest release, 1.59.0.

Along with applying the patch, users should also ensure they are using the `grpc.MaxConcurrentStreams` server option to apply a limit to the server's resources used for any single connection.

### Workarounds
None.

### References
#6703

## References
- https://github.com/grpc/grpc-go/security/advisories/GHSA-m425-mq94-257g
- https://nvd.nist.gov/vuln/detail/CVE-2023-44487
- https://github.com/grpc/grpc-go/pull/6703
- https://github.com/grpc/grpc-go/commit/f2180b4d5403d2210b30b93098eb7da31c05c721
- https://github.com/grpc/grpc-go
