# [H] OpenClaw: Workspace .env CLOUDSDK_PYTHON could influence Gmail setup gcloud execution

## Summary
Severity: High
Advisory: GHSA-fq9j-vw4w-fr6v
CVE: CVE-2026-53842
CWE: CWE-426
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-fq9j-vw4w-fr6v
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.2

## Details
### Summary

Workspace .env CLOUDSDK_PYTHON could influence Gmail setup gcloud execution. In affected versions, a workspace `.env` in a repository opened by a trusted operator could influence which Python runtime `gcloud` used through `CLOUDSDK_PYTHON`.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could run setup through an unintended local Python path. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.2`.

### Mitigations

run Gmail setup from trusted workspaces and clear workspace env overrides until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-fq9j-vw4w-fr6v
- https://nvd.nist.gov/vuln/detail/CVE-2026-53842
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-arbitrary-python-runtime-execution-via-cloudsdk-python-environment-variable
