# [M] n8n: Authenticated SSRF via Dynamic Node Parameters Endpoints Allows Internal Network Access

## Summary
Severity: Medium
Advisory: GHSA-9w78-79q7-r4fp
CVE: CVE-2026-65593
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:H/SI:L/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-9w78-79q7-r4fp
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.64
- npm: `n8n` — affected >=2.30.0 <2.30.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.29.8

## Details
## Impact

Endpoints in `/rest/dynamic-node-parameters/` lacked authorization scopes, making it reachable by any authenticated user with no workflow creation or execution required.

By supplying an absolute URL in the routing configuration, a caller could override the node type's declared baseURL, defeating the restriction meant to confine requests to the node's own upstream service. With SSRF protection disabled by default (`N8N_SSRF_PROTECTION_ENABLED=false`), this let an authenticated user make the n8n server issue HTTP requests to arbitrary internal targets.

## Patches
The issue has been fixed in n8n versions 1.123.64, 2.29.8, and 2.30.1. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict n8n instance access to fully trusted users only.
- Set `N8N_SSRF_PROTECTION_ENABLED=true` to enable SSRF filtering for private IP ranges and cloud metadata endpoints.
- Restrict network egress from the n8n host to limit reachable internal services.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-9w78-79q7-r4fp
- https://nvd.nist.gov/vuln/detail/CVE-2026-65593
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.64
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.29.8
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.30.1
- https://www.vulncheck.com/advisories/n8n-before-ssrf-via-dynamic-node-parameters
