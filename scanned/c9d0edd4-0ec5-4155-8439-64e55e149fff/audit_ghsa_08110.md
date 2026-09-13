# [H] OpenClaw Google Chat shared-path webhook target ambiguity allowed cross-account policy-context misrouting

## Summary
Severity: High
Advisory: GHSA-rq6g-px6m-c248
CVE: CVE-2026-28469
CWE: CWE-284, CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-rq6g-px6m-c248
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14
- npm: `clawdbot` — affected >=0

## Details
## Summary
When multiple Google Chat webhook targets are registered on the same HTTP path, and request verification succeeds for more than one target, inbound webhook events could be routed by first-match semantics. This can cause cross-account policy/context misrouting.

## Affected Packages / Versions
- npm: `openclaw` <= 2026.2.13
- npm: `clawdbot` <= 2026.1.24-3

## Details
Affected component: `extensions/googlechat/src/monitor.ts`.

Baseline behavior allowed multiple webhook targets per path and selected the first target that passed `verifyGoogleChatRequest(...)`. In shared-path deployments where multiple targets can verify successfully (for example, equivalent audience validation), inbound events could be processed under the wrong account context (wrong allowlist/session/policy).

## Fix
- Fix commit (merged to `main`): `61d59a802869177d9cef52204767cd83357ab79e`
- `openclaw` will be patched in the next planned release: `2026.2.14`.

`clawdbot` is a legacy/deprecated package name; no patched version is currently planned. Migrate to `openclaw` and upgrade to `openclaw >= 2026.2.14`.

## Workaround
Ensure each Google Chat webhook target uses a unique webhook path so routing is never ambiguous.

## Release Process Note
The advisory is pre-populated with the planned patched version. After the npm release is published, the remaining action should be to publish the advisory.

Thanks @vincentkoc for reporting.

---

Fix commit 61d59a802869177d9cef52204767cd83357ab79e confirmed on main and in v2026.2.14. Upgrade to `openclaw >= 2026.2.14`.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rq6g-px6m-c248
- https://nvd.nist.gov/vuln/detail/CVE-2026-28469
- https://github.com/openclaw/openclaw/commit/61d59a802869177d9cef52204767cd83357ab79e
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
- https://www.vulncheck.com/advisories/openclaw-cross-account-policy-context-misrouting-via-shared-webhook-path-ambiguity
