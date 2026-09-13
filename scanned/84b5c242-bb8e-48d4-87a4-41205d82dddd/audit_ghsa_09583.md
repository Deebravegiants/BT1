# [M] Flowise: SSRF Protection Bypass via Direct node-fetch / axios Usage (Patch Enforcement Failure)

## Summary
Severity: Medium
Advisory: GHSA-qqvm-66q4-vf5c
CVE: CVE-2026-43995
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-qqvm-66q4-vf5c
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.0
- npm: `flowise-components` — affected >=0 <3.1.0

## Details
### Summary

Flowise introduced SSRF protections through a centralized HTTP security wrapper (`httpSecurity.ts`) that implements deny-list validation and IP pinning logic.

However, multiple tool implementations directly import and invoke raw HTTP clients (`node-fetch`, `axios`Instead of using the secured wrapper.

Because enforcement is neither mandatory nor centralized, these tools bypass SSRF mitigation entirely, restoring full SSRF capability even after the patch.

This issue is distinct from specification trust issues and represents incomplete mitigation of previously addressed SSRF vulnerabilities.

### Details
**Intended Security Model:**

All outbound HTTP requests should pass through the centralized validation layer implemented in:

```
packages/components/src/httpSecurity.ts
```

This layer performs:

- `HTTP_DENY_LIST` enforcement
- IP resolution validation
- IP pinning
- Loopback blocking

**Observed Implementation Gap:**

Multiple tools bypass this layer and import HTTP libraries directly.

Examples include:

- `packages/components/nodes/tools/OpenAPIToolkit/OpenAPIToolkit.ts`
- `packages/components/nodes/tools/WebScraperTool/WebScraperTool.ts`
- `packages/components/nodes/tools/MCP/core.ts`
- `packages/components/nodes/tools/Arxiv/core.ts`

These files directly execute:

```
importfetchfrom'node-fetch'
```

or invoke `axios` without passing through the centralized validation wrapper.

Because there is no global interceptor or enforcement mechanism, outbound requests in these components are executed without SSRF validation.

This renders the mitigation introduced in GHSA-2x8m-83vc-6wv4 incomplete.

### Root Cause

Security enforcement is not centralized.

Outbound request validation depends on voluntary usage of a wrapper function rather than being structurally enforced.

Because direct imports of HTTP clients are allowed, the mitigation is easily bypassed.

This is an architectural enforcement failure rather than a single implementation bug.

### PoC
Even when an administrator configures:

```
HTTP_DENY_LIST=169.254.0.0/16,127.0.0.0/8
```

The following attack succeeds if a vulnerable tool is enabled:

**Chat Prompt:**

```
Use the Web Scraper tool to retrieve:
http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

Execution flow:

1. The LLM triggers `WebScraperTool`.
2. The tool calls raw `fetch()` directly.
3. No `httpSecurity.ts` validation is applied.
4. The request reaches the metadata endpoint.
5. The response is returned to the chat context.

This demonstrates that SSRF protection is opt-in rather than enforced.
### Impact

**Severity:** Critical (CVSS v3.1: 9.1 – AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)

This issue:

- Completely bypasses the centralized SSRF mitigation.
- Allows access to internal network resources.
- Enables the exploitation of cloud metadata and credential theft.
- Invalidates the security assumptions of the recent patch.

Any deployment enabling affected tools remains vulnerable.

### Recommended Remediation

1. Refactor all tools to use the centralized `secureFetch()` wrapper.
2. Add ESLint `no-restricted-imports` rules to prohibit the direct usage of `node-fetch` or `axios` in tool components.
3. Consider implementing a single internal HTTP client abstraction layer.
4. Apply network-level egress filtering as defense-in-depth.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-qqvm-66q4-vf5c
- https://nvd.nist.gov/vuln/detail/CVE-2026-43995
- https://github.com/FlowiseAI/Flowise
