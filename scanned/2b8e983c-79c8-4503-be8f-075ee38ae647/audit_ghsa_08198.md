# [M] utcp-http vulnerable to SSRF via attacker-controlled OpenAPI servers[0].url in HTTP communication protocol

## Summary
Severity: Medium
Advisory: GHSA-39j6-4867-gg4w
CVE: CVE-2026-44661
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-39j6-4867-gg4w
Type: github-advisory

## Affected
- PyPI: `utcp-http` — affected >=0 <1.1.2

## Details
## Summary

The `utcp-http` plugin is vulnerable to a blind Server-Side Request Forgery (SSRF) caused by a trust-boundary inconsistency between manual discovery and tool invocation. `register_manual()` validates the discovery URL against an HTTPS / loopback allowlist, but `call_tool()` and `call_tool_streaming()` reuse the resolved `tool_call_template.url` directly without revalidating. An attacker who hosts a malicious OpenAPI spec on a legitimate HTTPS endpoint can declare `servers: [{ url: "http://169.254.169.254" }]` (or any internal address) in the spec; the OpenAPI converter blindly trusts that value and the tool becomes a blind SSRF primitive that exposes cloud metadata, internal services, and other firewalled-only endpoints to the LLM caller.

All three HTTP-class protocols (`utcp_http.http`, `utcp_http.streamable_http`, `utcp_http.sse`) shared the same gap, plus a separate prefix-bypass: the previous `startswith("http://localhost")` check let URLs like `http://localhost.evil.com` through.

## Impact

A remote attacker who can convince the agent (via the LLM context, prompt injection, or a tool-discovery surface) to register their HTTPS OpenAPI URL can:
- Map internal networks behind the agent.
- Read AWS/GCP IAM credentials from cloud metadata endpoints (`http://169.254.169.254`, `http://metadata.google.internal`).
- Reach unauthenticated internal services (Elasticsearch, Redis HTTP, internal admin panels).
- Have responses returned to the LLM, which combined with prompt injection enables exfiltration back to the attacker.

## Affected versions

`utcp-http <= 1.1.1`.

## Patched versions

`utcp-http 1.1.2`.

## Patch

Commit: 5b16e43 on `dev`.

- New `utcp_http._security` helper: `ensure_secure_url(url, context=...)` parses the URL with `urllib.parse.urlparse` and validates the hostname (not a string prefix) against the loopback set, closing the `localhost.evil.com` bypass.
- All three protocols call `ensure_secure_url(url, context="manual discovery")` in `register_manual` (replacing the duplicated prefix check) and `ensure_secure_url(url, context="tool invocation")` immediately before each aiohttp request in `call_tool` / `call_tool_streaming`. The runtime check is the actual SSRF fix.
- New regression tests in `test_security.py` pin the accept/reject decisions and explicitly cover the historical bypass cases.

## Workarounds

For users who cannot upgrade immediately:
- Refuse to call `register_manual` with any URL controlled by an untrusted party, even over HTTPS.
- Restrict outbound network access from the host running the agent so internal addresses (RFC1918, 169.254.0.0/16, loopback for cloud metadata) are unreachable.

## Credit

Discovered and reported by [@YLChen-007](https://github.com/YLChen-007) in #83.

## References
- https://github.com/universal-tool-calling-protocol/python-utcp/security/advisories/GHSA-39j6-4867-gg4w
- https://nvd.nist.gov/vuln/detail/CVE-2026-44661
- https://github.com/universal-tool-calling-protocol/python-utcp
