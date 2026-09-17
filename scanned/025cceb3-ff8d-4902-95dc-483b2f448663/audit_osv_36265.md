# [M] OpenViking < 0.3.4 SSRF via /api/v1/resources

## Summary
Severity: Medium
Advisory: CVE-2026-22681
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-22681
Type: osv

## Details
OpenViking before 0.3.4 contains a server-side request forgery vulnerability that allows authenticated low-privilege attackers to access internal network services by submitting arbitrary URLs to the resources API endpoint. Attackers can POST a crafted URL to /api/v1/resources, causing the server to issue outbound HEAD and GET requests with redirects enabled to loopback, RFC 1918, link-local, or cloud metadata addresses, then read back responses through normal content APIs to enumerate and interact with internal services.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22681.json
- https://github.com/volcengine/OpenViking/releases/tag/v0.3.4
- https://nvd.nist.gov/vuln/detail/CVE-2026-22681
- https://www.vulncheck.com/advisories/openviking-ssrf-via-api-v1-resources
- https://github.com/volcengine/OpenViking/pull/1133
- https://github.com/volcengine/OpenViking/commit/41e345896d247e43ab78bbcb38b4a5b1b38ef62c
- https://github.com/volcengine/OpenViking
- https://github.com/volcengine/OpenViking/pull/1133https://github.com/volcengine/OpenViking/pull/1133
