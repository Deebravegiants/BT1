# [H] OpenClaw: QQBot streaming command could mutate config without explicit allowFrom

## Summary
Severity: High
Advisory: GHSA-jvm4-4j77-39p6
CVE: CVE-2026-53833
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-jvm4-4j77-39p6
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.29

## Details
### Summary

QQBot streaming command could mutate config without explicit allowFrom. In affected versions, a QQBot sender reaching the affected command could change configuration without requiring an explicit non-wildcard allowlist entry.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could modify QQBot streaming configuration outside the intended admin policy. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.4.29`.

### Mitigations

disable the command or restrict it to explicit trusted QQBot senders until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jvm4-4j77-39p6
- https://nvd.nist.gov/vuln/detail/CVE-2026-53833
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-via-qqbot-streaming-command
