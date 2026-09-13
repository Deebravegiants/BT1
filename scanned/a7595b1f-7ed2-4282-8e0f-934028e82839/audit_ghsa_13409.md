# [H] Connection confusion in gRPC

## Summary
Severity: High
Advisory: GHSA-cfgp-2977-2fmm
CVE: CVE-2023-32731
CWE: CWE-440
Ecosystem: Maven, PyPI, RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2023-07-05
Source: https://github.com/advisories/GHSA-cfgp-2977-2fmm
Type: github-advisory

## Affected
- Maven: `io.grpc:grpc-protobuf` — affected >=1.53.0 <1.53.1
- PyPI: `grpcio` — affected >=1.53.0 <1.53.1
- RubyGems: `grpc` — affected >=1.53.0 <1.53.1
- PyPI: `grpcio` — affected >=1.54.0 <1.54.2
- RubyGems: `grpc` — affected >=1.54.0 <1.54.2
- Maven: `io.grpc:grpc-protobuf` — affected >=1.54.0 <1.54.2

## Details
When gRPC HTTP2 stack raised a header size exceeded error, it skipped parsing the rest of the HPACK frame. This caused any HPACK table mutations to also be skipped, resulting in a desynchronization of HPACK tables between sender and receiver. If leveraged, say, between a proxy and a backend, this could lead to requests from the proxy being interpreted as containing headers from different proxy clients - leading to an information leak that can be used for privilege escalation or data exfiltration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32731
- https://github.com/grpc/grpc/issues/33463
- https://github.com/grpc/grpc/pull/32309
- https://github.com/grpc/grpc/pull/33005
- https://github.com/grpc/grpc/commit/29d8beee0ac2555773b2a2dda5601c74a95d6c10
- https://github.com/grpc/grpc/commit/65a2a895afaf1d2072447b9baf246374b182a946
- https://github.com/grpc/grpc/releases/tag/v1.53.1
- https://github.com/grpc/grpc/releases/tag/v1.54.2
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/grpc/CVE-2023-32731.yml
