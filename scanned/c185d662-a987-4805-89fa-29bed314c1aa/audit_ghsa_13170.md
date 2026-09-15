# [H] Denial of Service Vulnerability in gRPC TCP Server (Posix-compatible platforms)

## Summary
Severity: High
Advisory: GHSA-p25m-jpj4-qcrr
CVE: CVE-2023-4785
CWE: CWE-248
Ecosystem: PyPI, RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-13
Source: https://github.com/advisories/GHSA-p25m-jpj4-qcrr
Type: github-advisory

## Affected
- RubyGems: `grpc` — affected >=1.56.0 <1.56.2
- RubyGems: `grpc` — affected >=1.55.0 <1.55.3
- RubyGems: `grpc` — affected >=1.54.0 <1.54.3
- RubyGems: `grpc` — affected >=1.53.0 <1.53.2
- PyPI: `grpcio` — affected >=1.55.0 <1.55.3
- PyPI: `grpcio` — affected >=1.54.0 <1.54.3
- PyPI: `grpcio` — affected >=1.53.0 <1.53.2

## Details
Lack of error handling in the TCP server in Google's gRPC starting version 1.23 on posix-compatible platforms (ex. Linux) allows an attacker to cause a denial of service by initiating a significant number of connections with the server. Note that gRPC C++ Python, and Ruby are affected, but gRPC Java, and Go are NOT affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4785
- https://github.com/grpc/grpc/pull/33656
- https://github.com/grpc/grpc/pull/33667
- https://github.com/grpc/grpc/pull/33669
- https://github.com/grpc/grpc/pull/33670
- https://github.com/grpc/grpc/pull/33672
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/grpc/CVE-2023-4785.yml
- https://groups.google.com/g/grpc-io/c/LlLkB1CeE4U
- https://rubygems.org/gems/grpc/versions/1.53.2
- https://rubygems.org/gems/grpc/versions/1.54.3
- https://rubygems.org/gems/grpc/versions/1.55.3
- https://rubygems.org/gems/grpc/versions/1.56.2
