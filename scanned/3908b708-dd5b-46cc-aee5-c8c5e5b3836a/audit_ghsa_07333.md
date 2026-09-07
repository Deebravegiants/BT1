# [M] OpenClaw: memory-wiki ingest could read local files with operator.write scope

## Summary
Severity: Medium
Advisory: GHSA-p2fh-f5fc-44hr
CWE: CWE-732
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-p2fh-f5fc-44hr
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.12

## Details
### Summary

memory-wiki ingest could read local files with operator.write scope. In affected versions, a Gateway caller with `operator.write` access to the plugin tool could read arbitrary local file paths instead of staying within the intended ingest sources.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could import local file content into wiki memory. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Resolution

Update to a patched OpenClaw release when one is listed for this advisory. If the Patched versions field is populated, use that version or later.

### Mitigations

limit memory-wiki write access to trusted operators until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-p2fh-f5fc-44hr
- https://github.com/openclaw/openclaw
