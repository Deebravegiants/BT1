# [H] Pydantic AI has Stored XSS via Path Traversal in Web UI CDN URL

## Summary
Severity: High
Advisory: GHSA-wjp5-868j-wqv7
CVE: CVE-2026-25640
CWE: CWE-22, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-wjp5-868j-wqv7
Type: github-advisory

## Affected
- PyPI: `pydantic-ai` — affected >=1.34.0 <1.51.0
- PyPI: `pydantic-ai-slim` — affected >=1.34.0 <1.51.0

## Details
## Summary

A Path Traversal vulnerability in the [Pydantic AI web UI](https://ai.pydantic.dev/web/) allows an attacker to serve arbitrary JavaScript in the context of the application by crafting a malicious URL. If a victim clicks the link or visits it via an iframe, attacker-controlled code executes in their browser, enabling theft of chat history and other client-side data.

**This vulnerability only affects applications that use:**
- **`Agent.to_web`** to serve a chat interface
- **`clai web`** to serve a chat interface from the CLI

These are typically run locally (on `localhost`), but may also be deployed on a remote server.

### Description

The web UI serves its frontend HTML by fetching it from a CDN. In affected versions, the CDN URL is constructed using a `version` query parameter from the request URL. This parameter is not validated, allowing path traversal sequences that cause the server to fetch and serve attacker-controlled HTML/JavaScript from an arbitrary source on the same CDN, instead of the legitimate chat UI package.

### Who Is Affected

Projects are affected if your application uses `Agent.to_web` or `clai web` to serve the Pydantic AI chat interface.

### Attack Scenario

1. An attacker crafts a URL pointing to the victim's Pydantic AI web UI instance (either `localhost` with the known port, or a remote server endpoint) with a malicious `version` query parameter containing path traversal sequences.

2. The attacker gets the victim to visit this URL — directly via a link, through a redirect, or by embedding it in an iframe.

3. When the victim's browser loads the page, the server fetches and serves attacker-controlled HTML/JavaScript instead of the legitimate chat UI.

4. The attacker's JavaScript executes in the victim's browser in the context of the Pydantic AI web application, with access to:
   - **Chat history** stored in `localStorage` (all user messages and AI responses)
   - **Session cookies** that are not set as `HttpOnly`, if authentication middleware is configured

## Remediation

### Upgrade to Patched Version

**Upgrade** to the patched version or later. The fix removes the user-controllable `version` parameter entirely. The CDN URL is now hardcoded at startup and cannot be influenced by request parameters.

A new `html_source` parameter is available on `Agent.to_web` and `create_web_app` for applications that need to customize the UI source (e.g., for enterprise environments, offline usage, or custom UI builds). This parameter is only settable in application code, not via query parameters.

## References
- https://github.com/pydantic/pydantic-ai/security/advisories/GHSA-wjp5-868j-wqv7
- https://nvd.nist.gov/vuln/detail/CVE-2026-25640
- https://github.com/pydantic/pydantic-ai
- https://github.com/pydantic/pydantic-ai/releases/tag/v1.51.0
