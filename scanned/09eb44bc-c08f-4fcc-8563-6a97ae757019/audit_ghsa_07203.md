# [M] OpenClaw: Skill Workshop apply flow could override pending approval

## Summary
Severity: Medium
Advisory: GHSA-cqwv-9qjx-vxw2
CWE: CWE-807
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-cqwv-9qjx-vxw2
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.6

## Details
### Summary

Skill Workshop apply flow could override pending approval. In affected versions, an agent tool call reaching the affected Skill Workshop apply path could set `apply: true` despite `approvalPolicy: pending`.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could apply a workshop change before the expected approval step. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.6`.

### Mitigations

review Skill Workshop changes manually and keep the tool restricted until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-cqwv-9qjx-vxw2
- https://github.com/openclaw/openclaw
