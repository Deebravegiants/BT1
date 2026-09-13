# [M] Airtable MCP CLI before 0.2.5 Credential Disclosure via Unvalidated Configured Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-81101
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81101
Type: osv

## Details
The configure command accepted any endpoint URL and stored it beside the user's access token. ConfigureCommand.execute in src/cli.ts persisted the value given to its endpoint option into the user profile without passing it through createSafeUrl in src/config.ts, the helper that already restricted the environment-variable form of the same setting to the vendor's own hosts over HTTPS. Because the connect path in src/mcp.ts attaches the stored token as a bearer credential on every request to the configured endpoint, a user who was persuaded to run configure with an endpoint of the attacker's choosing sent their personal access token to that destination on each subsequent invocation. Version 0.2.5 applies the same helper to the option.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81101.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81101
- https://www.vulncheck.com/advisories/airtable-mcp-cli-before-0.2.5-credential-disclosure-via-unvalidated-configured-endpoint
- https://github.com/Airtable/airtable-mcp-cli/pull/17
- https://github.com/Airtable/airtable-mcp-cli
