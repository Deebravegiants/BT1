# [H] OpenClaw: Host environment sanitizer missed two Node.js control variables

## Summary
Severity: High
Advisory: GHSA-ccwh-wwpp-6wg5
CVE: CVE-2026-53864
CWE: CWE-184
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-ccwh-wwpp-6wg5
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.26

## Details
### Summary

Host environment sanitizer missed two Node.js control variables. In affected versions, a lower-trust env source such as a workspace `.env`, tool env override, or skill env block could pass Node.js control variables through the shared sanitizer.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could influence a later Node.js child process or coverage output path when that process is launched under the accepted environment. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.26`.

### Mitigations

avoid inheriting workspace or tool-supplied env values from untrusted repositories until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-ccwh-wwpp-6wg5
- https://nvd.nist.gov/vuln/detail/CVE-2026-53864
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-insufficient-environment-variable-sanitization-in-node-js-control-variables
