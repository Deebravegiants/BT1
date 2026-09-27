# [H] OpenClaw: Workspace .env npm_execpath could influence bundled runtime dependency install

## Summary
Severity: High
Advisory: GHSA-24vr-rprv-67rf
CVE: CVE-2026-53846
CWE: CWE-426
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-24vr-rprv-67rf
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.29

## Details
### Summary

Workspace .env npm_execpath could influence bundled runtime dependency install. In affected versions, a workspace `.env` in a repository opened by a trusted operator could override the package-manager executable path used by the install helper.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could run an unintended local package-manager executable during dependency setup. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.4.29`.

### Mitigations

install bundled runtime dependencies from trusted workspaces until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-24vr-rprv-67rf
- https://nvd.nist.gov/vuln/detail/CVE-2026-53846
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-arbitrary-package-manager-execution-via-workspace-env-npm-execpath
