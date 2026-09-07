# [M] OpenClaw: Slack reaction events could ignore reaction notification settings

## Summary
Severity: Medium
Advisory: GHSA-fcvx-5cxc-v5p8
CVE: CVE-2026-53851
CWE: CWE-285
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-fcvx-5cxc-v5p8
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.12

## Details
### Summary

Slack reaction events could ignore reaction notification settings. In affected versions, a Slack reaction event delivered to the configured app could enter the agent pipeline even when reaction notifications were disabled.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could trigger unintended agent processing for reaction events. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.12`.

### Mitigations

disable or restrict Slack reaction event subscriptions until patched if this path is not needed. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-fcvx-5cxc-v5p8
- https://nvd.nist.gov/vuln/detail/CVE-2026-53851
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-slack-reaction-event-notification-bypass
