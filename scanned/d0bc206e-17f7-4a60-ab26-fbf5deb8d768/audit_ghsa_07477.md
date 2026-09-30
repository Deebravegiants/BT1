# [H] OpenClaw: Hook-triggered CLI runs could receive owner MCP tool authority

## Summary
Severity: High
Advisory: GHSA-6fvr-66p3-3qj4
CVE: CVE-2026-53814
CWE: CWE-200, CWE-266, CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-6fvr-66p3-3qj4
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.20

## Details
### Summary

OpenClaw hook ingress can start automated agent runs using a configured hook token. In affected releases, a hook-triggered run could select a bundled CLI backend that received owner-scoped MCP loopback authority instead of a scope appropriate for hook ingress.

This issue affects the boundary between hook-token automation and owner-only MCP tools. It does not affect deployments with hooks disabled.

### Affected configurations

This affects deployments where hooks are enabled, `/hooks/agent` is reachable with a valid hook token, and a bundled CLI backend can be selected for the hook-triggered run.

### Impact

A caller with the hook token could cause the spawned CLI runtime to see or call MCP tools that should have been owner-only. The practical impact depends on which MCP tools are available; the reported proof used persistent cron state as a representative owner-only action.

### Patched Versions

The first stable patched version is `2026.5.20`.

Fixed in the `2026.5.20` stable release.

### Mitigations

Upgrade to `openclaw@2026.5.20` or later. Keep hook tokens secret, restrict network access to hook endpoints, and disable hooks when they are not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-6fvr-66p3-3qj4
- https://nvd.nist.gov/vuln/detail/CVE-2026-53814
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-privilege-escalation-via-hook-triggered-cli-mcp-tool-authority
