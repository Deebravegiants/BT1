# [H] eml_parser vulnerable to DoS via deeply nested parens in Received headers

## Summary
Severity: High
Advisory: GHSA-g7gc-gmgp-wgqg
CVE: CVE-2026-55620
CWE: CWE-770, CWE-1124
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-g7gc-gmgp-wgqg
Type: github-advisory

## Affected
- PyPI: `eml_parser` — affected >=0 <3.0.2

## Details
### Summary

`eml_parser` strips parenthesised CFWS comments from `Received:` headers using a regex-based fix-point loop. The loop has quadratic time complexity in the number of nested parens. A single `Received:` header containing 5,000 nested parens causes ~1.3 seconds of CPU saturation per parsed message; runtime quadruples per doubling of nesting depth.

### Impact

This represents a CPU exhaustion DoS in any pipeline that processes attacker-supplied EML files. An attacker can create relatively small EML files that will take multiple seconds to parse.

This is particularly problematic for synchronous email-processing pipelines (gateways, sandboxes, real-time triage) where worker latency directly translates to queue backpressure and possible service-level outages.

### Patches

Since version 3.0.2, `eml_parser` uses a linear-time algorithm to remove the comments from `Received:` headers.

## References
- https://github.com/GOVCERT-LU/eml_parser/security/advisories/GHSA-g7gc-gmgp-wgqg
- https://github.com/GOVCERT-LU/eml_parser/pull/90
- https://github.com/GOVCERT-LU/eml_parser/commit/746a69f86443eb0b6a47f77db3cfe727c21f92b3
- https://github.com/GOVCERT-LU/eml_parser
- https://github.com/GOVCERT-LU/eml_parser/releases/tag/v3.0.2
