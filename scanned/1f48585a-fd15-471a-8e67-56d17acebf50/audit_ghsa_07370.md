# [H] OpenClaw: Workspace .env could override Homebrew executable selection for skill install flows

## Summary
Severity: High
Advisory: GHSA-8wg3-5mcm-fjq8
CVE: CVE-2026-53819
CWE: CWE-426
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-8wg3-5mcm-fjq8
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.27

## Details
### Summary

Workspace .env could override Homebrew executable selection for skill install flows. In affected versions, a workspace `.env` in a repository opened by a trusted operator could override the Homebrew executable used by the install helper.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could run an unintended Homebrew-compatible executable during skill setup. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.27`.

### Mitigations

avoid running skill install flows from untrusted workspaces until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-8wg3-5mcm-fjq8
- https://nvd.nist.gov/vuln/detail/CVE-2026-53819
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-arbitrary-homebrew-executable-execution-via-workspace-env-override
