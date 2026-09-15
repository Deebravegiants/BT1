# [M] Denial of Service via Unrestricted Payload Buffering in MCP Toolbox

## Summary
Severity: Medium
Advisory: CVE-2026-14539
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/CVE-2026-14539
Type: osv

## Details
An allocation of resources without limits vulnerability in the HTTP handler component of Google mcp-toolbox versions up to and including 1.4.0 allows an unauthenticated attacker to cause a denial of service (DoS). The /mcp endpoint handler reads incoming payloads directly into system memory using an unrestricted buffer loop (io.ReadAll) without applying defensive constraints such as http.MaxBytesReader or pre-read Content-Length enforcement. By submitting a single, massive HTTP request body, an attacker can linearly consume available host memory until the runtime process is terminated by an Out-Of-Memory (OOM) error.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14539.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-14539
- https://github.com/googleapis/mcp-toolbox/pull/3216
