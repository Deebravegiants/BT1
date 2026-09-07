# [H] Excessive Iteration in gRPC

## Summary
Severity: High
Advisory: GHSA-496j-2rq6-j6cc
CVE: CVE-2023-33953
CWE: CWE-770, CWE-789
Ecosystem: PyPI, RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-08-09
Source: https://github.com/advisories/GHSA-496j-2rq6-j6cc
Type: github-advisory

## Affected
- PyPI: `grpcio` — affected >=0 <1.53.2
- PyPI: `grpcio` — affected >=1.54.0 <1.54.3
- PyPI: `grpcio` — affected >=1.55.0 <1.55.2
- PyPI: `grpcio` — affected >=1.56.0 <1.56.2
- RubyGems: `grpc` — affected >=0 <1.53.2
- RubyGems: `grpc` — affected >=1.54.0 <1.54.3
- RubyGems: `grpc` — affected >=1.55.0 <1.55.2
- RubyGems: `grpc` — affected >=1.56.0 <1.56.2

## Details
gRPC contains a vulnerability that allows hpack table accounting errors could lead to unwanted disconnects between clients and servers in exceptional cases/ Three vectors were found that allow the following DOS attacks:

- Unbounded memory buffering in the HPACK parser
- Unbounded CPU consumption in the HPACK parser

The unbounded CPU consumption is down to a copy that occurred per-input-block in the parser, and because that could be unbounded due to the memory copy bug we end up with an O(n^2) parsing loop, with n selected by the client.

The unbounded memory buffering bugs:

- The header size limit check was behind the string reading code, so we needed to first buffer up to a 4 gigabyte string before rejecting it as longer than 8 or 16kb.
- HPACK varints have an encoding quirk whereby an infinite number of 0’s can be added at the start of an integer. gRPC’s hpack parser needed to read all of them before concluding a parse.
- gRPC’s metadata overflow check was performed per frame, so that the following sequence of frames could cause infinite buffering: HEADERS: containing a: 1 CONTINUATION: containing a: 2 CONTINUATION: containing a: 3 etc…

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33953
- https://cloud.google.com/support/bulletins#gcp-2023-022
- https://github.com/advisories/GHSA-496j-2rq6-j6cc
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/grpc/CVE-2023-33953.yml
- https://security.snyk.io/vuln/SNYK-RUBY-GRPC-5834442
