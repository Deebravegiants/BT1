# [C] Pingora vulnerable to HTTP Request Smuggling via Premature Upgrade

## Summary
Severity: Critical
Advisory: GHSA-xq2h-p299-vjwv
CVE: CVE-2026-2833
CWE: CWE-444
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-xq2h-p299-vjwv
Type: github-advisory

## Affected
- crates.io: `pingora-core` — affected >=0 <0.8.0

## Details
### Impact
Pingora versions prior to 0.8.0 would immediately forward bytes following a request with an Upgrade header to the backend, without waiting for a 101 Switching Protocols response. This allows an attacker to smuggle requests to the backend and bypass proxy-level security controls.

This vulnerability primarily affects standalone Pingora deployments where a Pingora proxy is exposed to external traffic. An attacker could exploit this to bypass proxy-level ACL controls and WAF logic, poison caches and upstream connections, or perform cross-user attacks by hijacking sessions.

Note: Cloudflare customers and Cloudflare's CDN infrastructure were not affected by this vulnerability, as ingress proxies in the CDN stack maintain proper HTTP parsing boundaries and do not prematurely switch to upgraded connection forwarding mode.

### Patches
Pingora users should upgrade to Pingora v0.8.0 or higher, which fixes this issue by only switching connection modes after receiving a 101 Switching Protocols response from the backend (hash 824bdeefc61e121cc8861de1b35e8e8f39026ecd). Without a 101 response, subsequent bytes continue to be parsed as HTTP requests.

### Workarounds
As a workaround, users may return an error on requests with the Upgrade header present in their request filter logic in order to stop processing bytes beyond the request header and disable downstream connection reuse.

### References
See [CVE-2026-2833](https://www.cve.org/cverecord?id=CVE-2026-2833) and the [Cloudflare blog post](https://blog.cloudflare.com/pingora-oss-smuggling-vulnerabilities/) for more details.

### Credits
Disclosed responsibly by Rajat Raghav (@xclow3n) through the Cloudflare [Bug Bounty Program](https://www.cloudflare.com/disclosure/).

## References
- https://github.com/cloudflare/pingora/security/advisories/GHSA-xq2h-p299-vjwv
- https://nvd.nist.gov/vuln/detail/CVE-2026-2833
- https://github.com/cloudflare/pingora
- https://rustsec.org/advisories/RUSTSEC-2026-0033.html
