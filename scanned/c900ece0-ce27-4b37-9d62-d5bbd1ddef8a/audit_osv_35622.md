# [H] CVE-2026-11717

## Summary
Severity: High
Advisory: CVE-2026-11717
Aliases: GHSA-8fcc-w5hv-4gxv, GO-2026-5251
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-11717
Type: osv

## Details
An authentication bypass vulnerability exists in the generic opaque token validation path (validateOpaqueToken) of googleapis/mcp-toolbox.

When verifying an unparsed opaque token via an OAuth 2.0 introspection endpoint (RFC 7662), the toolbox decodes the response into an introspectResp struct where the Active field is declared as a pointer to a boolean (*bool). The code only explicitly rejects a token if the response contains a populated active field set to false (if introspectResp.Active != nil && !*introspectResp.Active). If an introspection endpoint responds with a payload that completely omits the mandatory active key, the internal variable remains nil, causing the conditional check to short-circuit. As a result, Toolbox accepts authorization tokens missing the "active" field, granting access to protected tools and underlying data sources.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11717.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11717
- https://github.com/googleapis/mcp-toolbox/pull/3341
