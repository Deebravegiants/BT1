# [C] LibreChat Exfiltrates Server Secrets via MCP Server URL Injection

## Summary
Severity: Critical
Advisory: CVE-2026-32625
Aliases: GHSA-4pcc-j6m6-wcwx
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-06-02
Source: https://osv.dev/vulnerability/CVE-2026-32625
Type: osv

## Details
LibreChat is an enhanced ChatGPT clone that supports multiple AI providers. In versions up to and including 0.8.3, the Model Context Protocol (MCP) server integration resolves ${VAR} placeholders against the server's process.env during Zod schema validation of user-supplied MCP server URLs. Any authenticated user can create a malicious MCP server configuration with a URL pointing to an attacker-controlled domain containing environment variable references, causing the LibreChat server to connect to the attacker's server and transmit critical secrets such as CREDS_KEY, CREDS_IV, JWT_SECRET, and MONGO_URI in the request URL. This enables full compromise of the installation's cryptographic materials and database credentials without requiring administrative privileges. This is patched in version 0.8.4-rc1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32625.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-4pcc-j6m6-wcwx
- https://nvd.nist.gov/vuln/detail/CVE-2026-32625
