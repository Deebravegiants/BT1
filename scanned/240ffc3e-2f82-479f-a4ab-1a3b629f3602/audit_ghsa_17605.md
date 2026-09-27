# [H] Pingora has a Request Smuggling Vulnerability

## Summary
Severity: High
Advisory: GHSA-93c7-7xqw-w357
CVE: CVE-2025-4366
CWE: CWE-444
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:A/VC:H/VI:H/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-06-20
Source: https://github.com/advisories/GHSA-93c7-7xqw-w357
Type: github-advisory

## Affected
- crates.io: `pingora-core` — affected >=0 <0.5.0

## Details
A request smuggling vulnerability identified within Pingora’s proxying framework, pingora-proxy, allows malicious HTTP requests to be injected via manipulated request bodies on cache HITs, leading to unauthorized request execution and potential cache poisoning.

### Fixed in
https://github.com/cloudflare/pingora/commit/fda3317ec822678564d641e7cf1c9b77ee3759ff 

### Impact
The issue could lead to request smuggling in cases where Pingora’s proxying framework, pingora-proxy, is used for caching allowing an attacker to manipulate headers and URLs in subsequent requests made on the same HTTP/1.1 connection.

## References
- https://github.com/cloudflare/pingora/security/advisories/GHSA-93c7-7xqw-w357
- https://nvd.nist.gov/vuln/detail/CVE-2025-4366
- https://github.com/cloudflare/pingora/commit/fda3317ec822678564d641e7cf1c9b77ee3759ff
- https://blog.cloudflare.com/resolving-a-request-smuggling-vulnerability-in-pingora
- https://github.com/cloudflare/pingora
- https://rustsec.org/advisories/RUSTSEC-2025-0037.html
