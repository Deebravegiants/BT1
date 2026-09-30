# [M] ha-mcp has XSS via Unescaped HTML in OAuth Consent Form

## Summary
Severity: Medium
Advisory: GHSA-pf93-j98v-25pv
CVE: CVE-2026-32112
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-pf93-j98v-25pv
Type: github-advisory

## Affected
- PyPI: `ha-mcp` — affected >=0 <7.0.0

## Details
### Summary

The ha-mcp OAuth consent form renders user-controlled parameters via Python f-strings with no HTML escaping. An attacker who can reach the OAuth endpoint and convince the server operator to follow a crafted authorization URL could execute JavaScript in the operator's browser. This affects only users running the beta OAuth mode (`ha-mcp-oauth`), which is not part of the standard setup and requires explicit configuration.

### Details

**Unescaped f-string rendering**

`consent_form.py` builds HTML using Python f-strings. No call to `html.escape()` exists anywhere in the file. The following values are rendered unescaped:

- `client_name` / `client_id` — in HTML element context (lines 299, 303)
- `client_id`, `redirect_uri`, `state` — in HTML attribute context (lines 310–312), where a `"` character breaks out of `value=""`
- `error_message`, `error`, `error_description` — in error display paths (lines 36–40, 496–497)

An attacker can register a client with a malicious `client_name` via the `/register` (DCR) endpoint, which accepts `client_name` without sanitization. If the server operator then visits a crafted authorization URL for that client, the payload executes in their browser.

**Open Dynamic Client Registration**

DCR is enabled by default with no initial access token required. This is intentional: Claude.ai and ChatGPT must self-register on first use, which is the standard MCP OAuth flow (RFC 7591). Requiring a pre-shared token would break those integrations. Registration alone grants no access — authorization requires an explicit action by the server operator.

### Impact

**Affected configuration:** OAuth mode only (`ha-mcp-oauth`, requires `MCP_BASE_URL`). This mode is in beta and is not included in the main setup documentation. The vast majority of ha-mcp users run stdio mode, which is not affected.

**Attack requirements:**
1. The attacker can reach the ha-mcp OAuth endpoint (it binds to `0.0.0.0` in HTTP mode)
2. The attacker registers a malicious client via `/register`
3. The attacker convinces the **server operator** — the person who set up ha-mcp — to follow a crafted authorization URL for an unrecognized application

Step 3 is a meaningful social engineering bar: the consent form displays the (unfamiliar) application name, and the operator has no legitimate reason to authorize an OAuth client they didn't initiate through Claude.ai or ChatGPT. Normal usage involves being redirected to the consent form from one of those platforms, not from an external link.

If exploited, a JavaScript payload could exfiltrate data entered into the consent form, including the Home Assistant Long-Lived Access Token.

### Fix

Upgrade to 7.0.0

## References
- https://github.com/homeassistant-ai/ha-mcp/security/advisories/GHSA-pf93-j98v-25pv
- https://nvd.nist.gov/vuln/detail/CVE-2026-32112
- https://github.com/homeassistant-ai/ha-mcp
