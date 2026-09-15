# [M] OpenClaw session tool visibility hardening and Telegram webhook secret fallback

## Summary
Severity: Medium
Advisory: GHSA-6hf3-mhgc-cm65
CVE: CVE-2026-27004
CWE: CWE-209, CWE-346
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-6hf3-mhgc-cm65
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.15

## Details
## Vulnerability

In some shared-agent deployments, OpenClaw session tools (`sessions_list`, `sessions_history`, `sessions_send`) allowed broader session targeting than some operators intended. This is primarily a configuration/visibility-scoping issue in multi-user environments where peers are not equally trusted.

In Telegram webhook mode, monitor startup also did not fall back to per-account `webhookSecret` when only the account-level secret was configured.

## Typical Use Case Context

Most regular OpenClaw deployments run a single agent, or run in trusted environments. In those setups, practical risk from this issue is generally low.

## Impact

- Shared-agent, multi-user, less-trusted environments: session-tool access could expose transcript content across peer sessions.
- Single-agent or trusted environments: practical impact is limited.
- Telegram webhook mode: account-level secret wiring could be missed unless an explicit monitor webhook secret override was provided.

## Affected Packages / Versions

- Package: npm `openclaw`
- Affected versions: `<= 2026.2.14`
- Patched version: `2026.2.15` (planned next release)

## Remediation

- Add and enforce `tools.sessions.visibility` (`self | tree | agent | all`) across session tools, defaulting to `tree`.
- Keep sandbox clamping behavior so sandboxed runs can be restricted to spawned/session-tree visibility.
- Resolve Telegram webhook secret from account config fallback in monitor webhook startup.

## Fix Commit(s)

- `c6c53437f7da033b94a01d492e904974e7bda74c`

Thanks @aether-ai-agent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-6hf3-mhgc-cm65
- https://nvd.nist.gov/vuln/detail/CVE-2026-27004
- https://github.com/openclaw/openclaw/commit/c6c53437f7da033b94a01d492e904974e7bda74c
- https://github.com/openclaw/openclaw
