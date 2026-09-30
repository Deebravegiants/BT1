# [H] OpenClaw: Slack interactive callbacks could skip configured sender checks in some shared-workspace flows

## Summary
Severity: High
Advisory: GHSA-x2ff-j5c2-ggpr
CVE: CVE-2026-32005
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-x2ff-j5c2-ggpr
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.25

## Details
## Impact

In shared Slack workspace deployments that rely on sender restrictions (`allowFrom`, DM policy, or channel user allowlists), some interactive callbacks (`block_action`, `view_submission`, `view_closed`) could be accepted before full sender authorization checks.

In that scenario, an unauthorized workspace member could enqueue system-event text into an active session. This issue did not provide unauthenticated access, cross-gateway isolation bypass, or host-level privilege escalation by itself.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Vulnerable versions: `<= 2026.2.24`
- Patched version: `2026.2.25` (planned next npm release)

## Fix Commit(s)

- `ce8c67c314b93f570f53c2a9abc124e1e3a54715`

## Release Process Note

`patched_versions` is pre-set to the release (`2026.2.25`). Advisory published with npm release `2026.2.25`.

## Trust Model Scope Note

OpenClaw does not support adversarial multi-user isolation on a single shared gateway instance. The supported model is one trust boundary per gateway (separate gateways/hosts for mutually untrusted users). See: https://docs.openclaw.ai/gateway/security

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-x2ff-j5c2-ggpr
- https://nvd.nist.gov/vuln/detail/CVE-2026-32005
- https://github.com/openclaw/openclaw/commit/ce8c67c314b93f570f53c2a9abc124e1e3a54715
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-in-interactive-callbacks-via-sender-check-skip
