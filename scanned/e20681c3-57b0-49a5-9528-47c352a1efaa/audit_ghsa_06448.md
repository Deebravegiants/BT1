# [H] OpenClaw: Fake package roots could influence memory-core artifact loading

## Summary
Severity: High
Advisory: GHSA-v8cx-933x-r976
CVE: CVE-2026-53813
CWE: CWE-427
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-v8cx-933x-r976
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.25

## Details
### Summary

Fake package roots could influence memory-core artifact loading. In affected versions, a local package root resolution path influenced by workspace state could select a package root that was not the intended bundled artifact root.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could load memory-core artifacts from an unintended local location. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.4.25`.

### Mitigations

run memory-core flows from trusted workspaces until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-v8cx-933x-r976
- https://nvd.nist.gov/vuln/detail/CVE-2026-53813
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-arbitrary-artifact-loading-via-fake-package-root-resolution
