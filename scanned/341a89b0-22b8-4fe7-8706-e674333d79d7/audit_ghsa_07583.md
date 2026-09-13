# [H] eBay API MCP Server Affected by Environment Variable Injection 

## Summary
Severity: High
Advisory: GHSA-97rm-xj73-33jh
CVE: CVE-2026-27203
CWE: CWE-15, CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-97rm-xj73-33jh
Type: github-advisory

## Affected
- npm: `ebay-mcp` — affected >=0

## Details
The `ebay_set_user_tokens` tool allows updating the `.env` file with new tokens. The `updateEnvFile` function in `src/auth/oauth.ts` blindly appends or replaces values without validating them for newlines or quotes. This allows an attacker to inject arbitrary environment variables into the configuration file.

### Impact
An attacker can inject arbitrary environment variables into the `.env` file. This could lead to:
- **Configuration Overwrites**: Attackers can overwrite critical settings like `EBAY_REDIRECT_URI` to hijack OAuth flows.
- **Denial of Service**: Injecting invalid configuration can prevent the server from starting.
- **Potential RCE**: In some environments, controlling environment variables (like `NODE_OPTIONS`) can lead to Remote Code Execution.

Found with [MCPwner](https://github.com/Pigyon/MCPwner) 🕶

## References
- https://github.com/YosefHayim/ebay-mcp/security/advisories/GHSA-97rm-xj73-33jh
- https://nvd.nist.gov/vuln/detail/CVE-2026-27203
- https://github.com/YosefHayim/ebay-mcp/commit/aab0bda75ea9dd27aa37d0d8524d7cf41b3c4a9a
- https://github.com/YosefHayim/ebay-mcp
