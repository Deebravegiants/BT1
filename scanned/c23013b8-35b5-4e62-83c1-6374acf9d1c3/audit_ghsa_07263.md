# [M] OpenClaw: Slack and Zalo webhook secrets could remain active after secrets.reload

## Summary
Severity: Medium
Advisory: GHSA-275c-xpvc-jgfw
CVE: CVE-2026-53830
CWE: CWE-613
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-275c-xpvc-jgfw
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.22

## Details
### Summary

Slack and Zalo webhook secrets could remain active after secrets.reload. In affected versions, a caller with an old webhook secret during the stale-secret window could keep accepting the previous secret after `secrets.reload`.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could deliver webhook events briefly after the operator expected revocation. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.4.22`.

### Mitigations

restart the affected channel runtime after rotating webhook secrets until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-275c-xpvc-jgfw
- https://nvd.nist.gov/vuln/detail/CVE-2026-53830
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-webhook-secret-revocation-bypass-via-secrets-reload
