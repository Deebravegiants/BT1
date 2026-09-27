# [H] Coder: Route hijacking through lack of validation of agent-supplied AllowedIPs in tailnet coordinator

## Summary
Severity: High
Advisory: GHSA-wrq8-fcv5-8hvp
CVE: CVE-2026-55428
CWE: CWE-285, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-wrq8-fcv5-8hvp
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=2.34.0 <2.34.2
- Go: `github.com/coder/coder/v2` — affected >=2.33.0 <2.33.8
- Go: `github.com/coder/coder/v2` — affected >=2.30.0 <2.32.7
- Go: `github.com/coder/coder/v2` — affected >=0 <2.29.17

## Details
### Summary

The tailnet coordinator validates that an agent's `Addresses` derive from its authenticated UUID but applies no equivalent check to `AllowedIPs`. The coordinator forwards agent-supplied `AllowedIPs` verbatim to tunnel peers which install them into the WireGuard peer configuration.

### Impact

A malicious workspace agent can advertise arbitrary `AllowedIPs` prefixes including another agent's tailnet address. Coder's `ServerTailnet` routes to agents by tailnet IP so an agent that claims a victim's prefix can intercept web terminal and workspace app traffic and serve spoofed content. Exploitation requires an authenticated user with a running workspace and a modified agent binary.

### Patches

The fix validates each `AllowedIPs` prefix against the authenticating agent's UUID just like `Addresses`.

The fix was backported to all supported release lines:

| Release line | Patched version |
|---|---|
| 2.34 | [v2.34.2](https://github.com/coder/coder/releases/tag/v2.34.2) |
| 2.33 | [v2.33.8](https://github.com/coder/coder/releases/tag/v2.33.8) |
| 2.32 | [v2.32.7](https://github.com/coder/coder/releases/tag/v2.32.7) |
| 2.29 (ESR) | [v2.29.17](https://github.com/coder/coder/releases/tag/v2.29.17) |

### Workarounds

Operators who cannot upgrade immediately should monitor coordinator logs for agents advertising unexpected `AllowedIPs` prefixes.

### Resources

- Fix: #26144

### Credits

Coder would like to thank Anthropic's Security Team (ANT-2026-22451) for independently disclosing this issue!

## References
- https://github.com/coder/coder/security/advisories/GHSA-wrq8-fcv5-8hvp
- https://github.com/coder/coder/pull/26144
- https://github.com/coder/coder
