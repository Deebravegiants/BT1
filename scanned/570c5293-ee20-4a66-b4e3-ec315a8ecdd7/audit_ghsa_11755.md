# [H] OpenClaw: Gateway /tools/invoke tool escalation + ACP permission auto-approval

## Summary
Severity: High
Advisory: GHSA-943q-mwmv-hhvh
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-943q-mwmv-hhvh
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
## Summary

OpenClaw Gateway exposes an authenticated HTTP endpoint (`POST /tools/invoke`) intended for invoking a constrained set of tools. Two issues could combine to significantly increase blast radius in misconfigured or exposed deployments:

- The HTTP gateway layer did not deny high-risk session orchestration tools by default, allowing a caller with Gateway auth to invoke tools like `sessions_spawn` / `sessions_send` and pivot into creating or controlling agent sessions.
- ACP clients could auto-approve permission requests for risky tools with insufficient user interaction/guardrails, reducing the friction that should normally prevent silent execution or mutation.

## Impact

If the Gateway is reachable by an attacker and they obtain a valid Gateway token, they may be able to:

- Escalate from single-tool invocation to spawning/controlling sessions and reach command execution capabilities depending on tool policy and runtime environment.
- Perform cross-session message injection via `sessions_send`.
- In ACP-integrated scenarios, obtain unintended approvals for non-read/search tool permissions.

## CVSS

- `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H` (8.8)

## Affected versions

- `openclaw < 2026.2.14`

## Fixed in

- `openclaw >= 2026.2.14`

## Remediation

The default behavior is now hardened:

- PR #15390: deny high-risk tools over HTTP `/tools/invoke` by default (with `gateway.tools.{allow,deny}` overrides) and harden ACP permission handling.
- Commit `bb1c3dfe1`: ACP clients now prompt for any non-read/search permission request (fail closed for mutating/execution/fetch operations).
- Commit `539689a2f`: security audit warns when `gateway.tools.allow` re-enables default-denied HTTP tools, since this can increase RCE blast radius if the Gateway is reachable.
- Commit `153a7644e`: ACP safe-kind inference is stricter to avoid accidental auto-approval due to substring matches (still auto-approves only confident `read/search`).

## Mitigations / deployment guidance

- Keep the Gateway loopback-only unless you have a strong reason not to: `gateway.bind="loopback"` / `openclaw gateway run --bind loopback`.
- Avoid exposing the Gateway directly to the public internet. Use an SSH tunnel or Tailscale to access a loopback-bound Gateway.
- Treat opting in to default-denied HTTP tools (via `gateway.tools.allow`) as high-risk and audit such configurations carefully.

## Credits

OpenClaw thanks @aether-ai-agent for reporting this issue and contributing remediation work.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-943q-mwmv-hhvh
- https://github.com/openclaw/openclaw/pull/15390
- https://github.com/openclaw/openclaw/commit/153a7644e
- https://github.com/openclaw/openclaw/commit/539689a2f
- https://github.com/openclaw/openclaw/commit/bb1c3dfe1
- https://github.com/openclaw/openclaw/commit/ee31cd47b49f4b2f128a69a2a3745ca9db68b3be
- https://github.com/openclaw/openclaw
