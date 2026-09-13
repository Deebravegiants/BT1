# [M] OpenClaw: Mattermost handlers could fall open when channel type was missing

## Summary
Severity: Medium
Advisory: GHSA-gp79-m99v-gjmh
CVE: CVE-2026-53837
CWE: CWE-636
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-gp79-m99v-gjmh
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.6

## Details
### Summary

Mattermost handlers could fall open when channel type was missing. In affected versions, a Mattermost event missing channel type metadata could continue without applying the intended DM policy decision.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could process a Mattermost event that should have been gated by channel policy. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.6`.

### Mitigations

keep Mattermost bot access restricted and review channel metadata errors until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-gp79-m99v-gjmh
- https://nvd.nist.gov/vuln/detail/CVE-2026-53837
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-missing-channel-type-validation-in-mattermost-event-handlers
