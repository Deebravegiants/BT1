# [H] TypeBot: Cross-Workspace Credential Theft via Bot-Engine Preview Endpoint

## Summary
Severity: High
Advisory: CVE-2026-39968
Aliases: GHSA-cq66-9cwr-x8jr
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-05-22
Source: https://osv.dev/vulnerability/CVE-2026-39968
Type: osv

## Details
TypeBot is a chatbot builder tool. In versions 3.15.2 and prior, the fix for GHSA-4xc5-wfwc-jw47 ("Credential Theft via Client-Side Script Execution and API Authorization Bypass") is incomplete. While the builder's getCredentials tRPC endpoint was patched with workspace membership checks, the bot-engine runtime still allows any authenticated user to use credentials from any workspace via the preview chat endpoint. The bot-engine's getCredentials() utility function uses a falsy check (if (workspaceId && ...)) for workspace ownership validation. Since the preview endpoint accepts a client-controlled workspaceId field and the Zod schema allows empty strings, an attacker can supply workspaceId: "" to bypass credential ownership verification entirely. Exploitation can result in credential exfiltration, external service abuse, financial damage and a data breach.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.16.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39968.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-cq66-9cwr-x8jr
- https://nvd.nist.gov/vuln/detail/CVE-2026-39968
- https://github.com/baptisteArno/typebot.io/commit/d96f572e6099c5f622c05ba7b8634e6477dcf052
