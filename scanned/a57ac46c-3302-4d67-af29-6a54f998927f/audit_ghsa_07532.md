# [H] OpenClaw: Scoped chat.send route inheritance could bypass admin command scope gates

## Summary
Severity: High
Advisory: GHSA-hw9r-h9mr-4jff
CWE: CWE-862, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-hw9r-h9mr-4jff
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.18

## Details
### Summary

Some internal command handlers require `operator.approvals` or `operator.admin` scopes. In affected releases, a scoped Gateway `chat.send` request delivered through an inherited external route could be evaluated as an external-channel command while still carrying the lower Gateway client scopes.

This issue affects scoped Gateway clients. It does not apply to shared-secret bearer HTTP compatibility endpoints, which are documented as full operator surfaces under OpenClaw's trust model.

### Affected configurations

This affects deployments where a scoped Gateway caller with `operator.write` can use `chat.send` with delivery into a session that has an inherited external delivery route.

### Impact

Commands that should have required `operator.approvals` or `operator.admin` could run with only `operator.write` in this routed context. Affected command families included approval resolution and selected administrative commands such as plugin, config, MCP, allowlist, and ACP mutations.

### Patched Versions

The first stable patched version is `2026.5.18`.

### Mitigations

Upgrade to `openclaw@2026.5.18` or later. Before upgrading, avoid granting `operator.write` tokens to clients that can deliver commands into sessions with external routes unless those clients are trusted with admin-like command effects.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-hw9r-h9mr-4jff
- https://github.com/openclaw/openclaw
