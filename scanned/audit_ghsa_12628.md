# [M] s2n-quic potential denial of service vulnerability when receiving empty UDP packets

## Summary
Severity: Medium
Advisory: GHSA-hxq4-mx37-fqvg
Ecosystem: crates.io
Published: 2023-06-30
Source: https://github.com/advisories/GHSA-hxq4-mx37-fqvg
Type: github-advisory

## Affected
- crates.io: `s2n-quic` — affected >=1.22.0 <1.23.0

## Details
### Impact

An issue in s2n-quic results in the endpoint shutting down after receiving an empty UDP packet on a connection. 

No AWS services are affected by this issue and customers of AWS services do not need to take action. Applications using s2n-quic should upgrade their application to the most recent release of s2n-quic.

Impacted version: s2n-quic v1.22.0.

### Patches

The patch is included in s2n-quic [v1.23.0](https://github.com/aws/s2n-quic/releases/tag/v1.23.0).

If you have any questions or comments about this advisory we ask that you contact AWS/Amazon Security via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/aws/s2n-quic/security/advisories/GHSA-hxq4-mx37-fqvg
- https://github.com/aws/s2n-quic/commit/4b1d417e9de7eafaf5350553c5fcb9264dfa32f5
- https://github.com/aws/s2n-quic
- https://github.com/aws/s2n-quic/releases/tag/v1.23.0
