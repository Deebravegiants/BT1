# [H] OpenClaw: Workspace .env STATE_DIRECTORY could influence bundled runtime dependency roots

## Summary
Severity: High
Advisory: GHSA-wc84-j36w-pw4x
CVE: CVE-2026-53858
CWE: CWE-426
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-wc84-j36w-pw4x
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.2

## Details
### Summary

Workspace .env STATE_DIRECTORY could influence bundled runtime dependency roots. In affected versions, a workspace `.env` in a repository opened by a trusted operator could set `STATE_DIRECTORY` before runtime dependency root resolution.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could load bundled runtime dependencies from an unintended local state path. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.2`.

### Mitigations

avoid opening untrusted workspace env files before runtime dependency installation until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-wc84-j36w-pw4x
- https://nvd.nist.gov/vuln/detail/CVE-2026-53858
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-arbitrary-runtime-dependency-loading-via-state-directory-environment-variable
