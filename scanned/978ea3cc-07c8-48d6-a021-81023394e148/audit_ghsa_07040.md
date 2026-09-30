# [H] OpenClaw: Exec approval display truncation could hide the command being approved

## Summary
Severity: High
Advisory: GHSA-xww8-gqvh-92x9
CWE: CWE-284, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-xww8-gqvh-92x9
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.18

## Details
### Summary

OpenClaw exec approvals could show a shortened command in the approval UI while keeping the full original command for execution. For very long commands, an approver could see and approve a benign-looking prefix while a hidden suffix remained part of the command that would run after approval.

This issue affects the approval display and binding for oversized exec commands. It does not make exec available to unauthenticated users, and it does not change OpenClaw's local-first trust model.

### Affected configurations

This affects deployments where exec approval is enabled and an authenticated caller can create a pending host exec request with a command long enough to be truncated in the approval view.

### Impact

An approver could make a decision from incomplete command text. If the hidden suffix contained additional shell operations, those operations could run after the approval was resolved.

The practical impact depends on who can request exec approvals and who is allowed to approve them. The issue is an approval integrity problem: the approval surface did not faithfully represent the command that would execute.

### Patched Versions

The first stable patched version is `2026.5.18`.

### Mitigations

Upgrade to `openclaw@2026.5.18` or later. Before upgrading, avoid approving unusually long exec commands and keep approval capability limited to trusted operators.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-xww8-gqvh-92x9
- https://github.com/openclaw/openclaw
