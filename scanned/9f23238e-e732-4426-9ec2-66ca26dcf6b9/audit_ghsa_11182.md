# [H] Micronaut Framework vulnerable to a Denial of Service in HTML error response caching

## Summary
Severity: High
Advisory: GHSA-2hcp-gjrf-7fhc
CVE: CVE-2026-33012
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-2hcp-gjrf-7fhc
Type: github-advisory

## Affected
- Maven: `io.micronaut:micronaut-http-server` — affected >=4.7.0 <4.10.17

## Details
`DefaultHtmlErrorResponseBodyProvider` in `io.micronaut:micronaut-http-server` since `4.7.0` and until `4.10.7` used an unbounded `ConcurrentHashMap` cache with no eviction policy. If the application throws an exception whose message may be influenced by an attacker, for example, including request query value parameters,  this could be used by remote attackers
to cause a denial of service (unbounded heap growth and OutOfMemoryError). 

Fixed via: https://github.com/micronaut-projects/micronaut-core/commit/1e2ba2c14386af3d47751732d02053a72b0b49b3

## References
- https://github.com/micronaut-projects/micronaut-core/security/advisories/GHSA-2hcp-gjrf-7fhc
- https://nvd.nist.gov/vuln/detail/CVE-2026-33012
- https://github.com/micronaut-projects/micronaut-core/commit/1e2ba2c14386af3d47751732d02053a72b0b49b3
- https://github.com/micronaut-projects/micronaut-core
- https://github.com/micronaut-projects/micronaut-core/releases/tag/v4.10.17
