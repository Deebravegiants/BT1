# [H] OpenClaw: QQBot native approval buttons did not enforce configured approver identity

## Summary
Severity: High
Advisory: GHSA-mgq6-vr84-7m2j
CVE: CVE-2026-35630
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-mgq6-vr84-7m2j
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.18

## Details
### Summary

OpenClaw's QQBot channel can deliver native approval buttons for exec and plugin approvals. In affected releases, the button callback path resolved approvals without enforcing the configured QQBot approver identity.

The text command approval path used the authorization check; the issue was specific to native QQBot approval buttons.

### Affected configurations

This affects deployments where QQBot native approval buttons are enabled and an approval message is visible to a QQ user who is not configured as an approver.

### Impact

A non-approver who could see the approval message could click an approval button and resolve the pending request. Depending on the pending approval, this could allow an exec or plugin action that should have required an authorized approver.

### Patched Versions

The first stable patched version is `2026.5.18`.

### Mitigations

Upgrade to `openclaw@2026.5.18` or later. Before upgrading, avoid delivering native approval buttons into QQ conversations that include users who should not be able to approve.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-mgq6-vr84-7m2j
- https://nvd.nist.gov/vuln/detail/CVE-2026-35630
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-qqbot-missing-approver-identity-enforcement-in-native-approval-buttons
