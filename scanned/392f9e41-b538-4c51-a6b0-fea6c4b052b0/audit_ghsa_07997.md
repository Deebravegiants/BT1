# [H] OpenClaw/Clawdbot has 1-Click RCE via Authentication Token Exfiltration From gatewayUrl

## Summary
Severity: High
Advisory: GHSA-g8p2-7wf7-98mq
CVE: CVE-2026-25253
CWE: CWE-668
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-g8p2-7wf7-98mq
Type: github-advisory

## Affected
- npm: `clawdbot` — affected >=0 <2026.1.29

## Details
## Summary

The Control UI trusts `gatewayUrl` from the query string without validation and auto-connects on load, sending the stored gateway token in the WebSocket connect payload.

Clicking a crafted link or visiting a malicious site can send the token to an attacker-controlled server. The attacker can then connect to the victim's local gateway, modify config (sandbox, tool policies), and invoke privileged actions, achieving 1-click RCE. This vulnerability is exploitable even on instances configured to listen on loopback only, since the victim's browser initiates the outbound connection.

## Details

The root cause is the lack of validation for `gatewayUrl` combined with auto‑connect behavior on page load. With the change users now need to confirm the new gateway URL in the UI.

## Impact

This is a token exfiltration vulnerability that leads to full gateway compromise. It impacts any Moltbot deployment where a user has authenticated to the Control UI. The attacker gains operator-level access to the gateway API, enabling arbitrary config changes and code execution on the gateway host. The attack works even when the gateway binds to loopback because the victim's browser acts as the bridge.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-g8p2-7wf7-98mq
- https://nvd.nist.gov/vuln/detail/CVE-2026-25253
- https://depthfirst.com/post/1-click-rce-to-steal-your-moltbot-data-and-keys
- https://github.com/openclaw/openclaw
- https://openclaw.ai/blog
