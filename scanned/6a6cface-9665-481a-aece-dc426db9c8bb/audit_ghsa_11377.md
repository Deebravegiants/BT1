# [C] Pingora has HTTP Request Smuggling via HTTP/1.0 and Transfer-Encoding Misparsing

## Summary
Severity: Critical
Advisory: GHSA-hj7x-879w-vrp7
CVE: CVE-2026-2835
CWE: CWE-444
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-hj7x-879w-vrp7
Type: github-advisory

## Affected
- crates.io: `pingora-core` — affected >=0 <0.8.0

## Details
### Impact
Pingora versions prior to 0.8.0 improperly allowed HTTP/1.0 request bodies to be close-delimited and incorrectly handled multiple Transfer-Encoding values. This allows an attacker to desync Pingora's request framing from backend servers and smuggle requests to the backend.

This vulnerability primarily affects standalone Pingora deployments in front of certain backends that accept HTTP/1.0 requests. An attacker could exploit this to bypass proxy-level ACL controls and WAF logic, poison caches and upstream connections, or perform cross-user attacks by hijacking sessions.

Note: Cloudflare customers and Cloudflare's CDN infrastructure were not affected by this vulnerability, as its ingress proxy layers rejected ambiguous framing such as invalid Content-Length values and internally forwarded non-ambiguous message length framing headers.

### Patches
Pingora users should upgrade to Pingora v0.8.0 or higher that fixes this issue by correctly parsing message length headers per RFC 9112 and strictly adhering to more RFC guidelines, including that HTTP request bodies are never close-delimited (commits 7f7166d62fa916b9f11b2eb8f9e3c4999e8b9023, 40c3c1e9a43a86b38adeab8da7a2f6eba68b83ad, and 87e2e2fb37edf9be33e3b1d04726293ae6bf2052).

### Workarounds
As a workaround, users can reject certain requests with an error in the request filter logic in order to stop processing bytes on the connection and disable downstream connection reuse. The user should reject any non-HTTP/1.1 request, or a request that has invalid Content-Length, multiple Transfer-Encoding headers, or Transfer-Encoding header that is not an exact “chunked” string match.

### References
See [CVE-2026-2835](https://www.cve.org/CVERecord?id=CVE-2026-2835) and the [Cloudflare blog post](https://blog.cloudflare.com/pingora-oss-smuggling-vulnerabilities/) for more details.

### Credits
Disclosed responsibly by Rajat Raghav (@xclow3n) through the Cloudflare [Bug Bounty Program](https://www.cloudflare.com/disclosure/).

## References
- https://github.com/cloudflare/pingora/security/advisories/GHSA-hj7x-879w-vrp7
- https://nvd.nist.gov/vuln/detail/CVE-2026-2835
- https://github.com/cloudflare/pingora
- https://rustsec.org/advisories/RUSTSEC-2026-0034.html
