# [M] OpenClaw: Config recovery could restore openclaw.json with broad file permissions

## Summary
Severity: Medium
Advisory: GHSA-rwp6-7w3q-75fq
CVE: CVE-2026-53856
CWE: CWE-276
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-rwp6-7w3q-75fq
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.4.23 <2026.4.24

## Details
### Summary

Config recovery could restore openclaw.json with broad file permissions. In affected versions, a local recovery path after configuration repair could leave the restored config file more readable than intended.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could expose local configuration to other same-host users where OS permissions allow it. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.4.24`.

### Mitigations

check `openclaw.json` permissions after recovery on shared hosts until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rwp6-7w3q-75fq
- https://nvd.nist.gov/vuln/detail/CVE-2026-53856
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-insecure-file-permissions-in-config-recovery-via-openclaw-json
