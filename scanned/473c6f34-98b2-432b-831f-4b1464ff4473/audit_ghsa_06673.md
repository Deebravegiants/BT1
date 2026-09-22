# [M] OpenClaw: MCP loopback could skip owner-only tool policy for non-owner callers

## Summary
Severity: Medium
Advisory: GHSA-rj6p-xmxr-qj4h
CVE: CVE-2026-53818
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-rj6p-xmxr-qj4h
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.24

## Details
### Summary

MCP loopback could skip owner-only tool policy for non-owner callers. In affected versions, a non-owner caller reaching the affected loopback path could skip owner-only tool policy and before-tool-call hooks.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could invoke owner-only behavior through that loopback path. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Resolution

Update to a patched OpenClaw release when one is listed for this advisory. If the Patched versions field is populated, use that version or later.

### Mitigations

restrict MCP loopback access to trusted operators until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rj6p-xmxr-qj4h
- https://nvd.nist.gov/vuln/detail/CVE-2026-53818
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-owner-only-tool-policy-bypass-via-mcp-loopback
