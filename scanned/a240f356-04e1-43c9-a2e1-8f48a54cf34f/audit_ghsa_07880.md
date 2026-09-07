# [M] Cloudflare Agents has a Reflected Cross-Site Scripting (XSS) vulnerability in AI Playground site

## Summary
Severity: Medium
Advisory: GHSA-w5cr-2qhr-jqc5
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:N/SC:H/SI:L/SA:N (CVSS_V4)
Published: 2026-02-13
Source: https://github.com/advisories/GHSA-w5cr-2qhr-jqc5
Type: github-advisory

## Affected
- npm: `agents` — affected >=0 <0.3.10

## Details
## Summary

A Reflected Cross-Site Scripting (XSS) vulnerability was discovered in the AI Playground's OAuth callback handler. The error_description query parameter was directly interpolated into an HTML script tag without proper escaping, allowing attackers to execute arbitrary JavaScript in the context of the victim's session.

### Root cause

The OAuth callback handler in `site/ai-playground/src/server.ts` directly interpolated the `authError` value, sourced from the `error_description` query parameter,  into an inline `<script>` tag.

### Impact

An attacker could craft a malicious link that, when clicked by a victim, would:
- Steal user chat message history 
- Access all LLM interactions stored in the user's session.
- Access connected MCP Servers 
- Interact with any MCP servers connected to the victim's session (public or authenticated/private), potentially allowing the attacker to perform actions on the victim's behalf

### Mitigation:

- PR: https://github.com/cloudflare/agents/pull/841
- Agents-sdk users should upgrade to `agents@0.3.10`
- Developers using `configureOAuthCallback` with custom error handling in their own applications should ensure all user-controlled input is escaped before interpolation.

### Credits

Disclosed responsibly by Nishant Kumawat

## References
- https://github.com/cloudflare/agents/security/advisories/GHSA-w5cr-2qhr-jqc5
- https://github.com/cloudflare/agents/pull/841
- https://github.com/cloudflare/agents/commit/3f490d045844e4884db741afbb66ca1fe65d4093
- https://github.com/cloudflare/agents
