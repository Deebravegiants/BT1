# [H] gRPC Reachable Assertion issue

## Summary
Severity: High
Advisory: GHSA-6628-q6j9-w8vg
CVE: CVE-2023-1428
CWE: CWE-617
Ecosystem: Maven, PyPI, RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-6628-q6j9-w8vg
Type: github-advisory

## Affected
- Maven: `io.grpc:grpc-protobuf` — affected >=1.51.0 <1.53.0
- PyPI: `grpcio` — affected >=1.51.0 <1.53.0
- RubyGems: `grpc` — affected >=1.51.0 <1.53.0

## Details
There exists an vulnerability causing an abort() to be called in gRPC. 
The following headers cause gRPC's C++ implementation to abort() when called via http2:

te: x (x != trailers)

:scheme: x (x != http, https)

grpclb_client_stats: x (x == anything)

On top of sending one of those headers, a later header must be sent that gets the total header size past 8KB. We recommend upgrading past git commit 2485fa94bd8a723e5c977d55a3ce10b301b437f8 or v1.53 and above.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1428
- https://github.com/grpc/grpc/issues/33463
- https://github.com/grpc/grpc/commit/2485fa94bd8a723e5c977d55a3ce10b301b437f8
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/grpc/CVE-2023-1428.yml
