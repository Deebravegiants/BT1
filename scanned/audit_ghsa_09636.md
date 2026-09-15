# [C] OpenClaw: Feishu webhook and card-action validation now fail closed

## Summary
Severity: Critical
Advisory: GHSA-xh72-v6v9-mwhc
CVE: CVE-2026-44109
CWE: CWE-1188, CWE-287, CWE-294
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-xh72-v6v9-mwhc
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.15

## Details
## Summary

Feishu webhook mode accepted missing `encryptKey` configuration as valid and blank card-action callback tokens as usable lifecycle tokens. Together, those fail-open paths could allow unauthenticated webhook or card-action traffic to reach command dispatch in affected deployments.

## Impact

A deployment using Feishu webhook mode without a configured `encryptKey`, or handling malformed card-action callbacks with blank callback tokens, could fail open instead of rejecting the request. Severity remains critical because affected webhook deployments expose a network-triggered path into OpenClaw command handling without the expected Feishu signature or replay protection.

## Affected versions

- Affected: `< 2026.4.15`
- Patched: `2026.4.15`

## Fix

OpenClaw `2026.4.15` makes Feishu webhook and card-action validation fail closed. Webhook mode now refuses to start without an `encryptKey`, missing signing configuration returns invalid instead of valid, invalid signatures return `401`, and blank card-action callback tokens are rejected before dispatch.

Verified in `v2026.4.15`:

- `extensions/feishu/src/monitor.transport.ts` returns invalid when `encryptKey` is missing, refuses webhook mode without `encryptKey`, and rejects invalid signatures before JSON handling.
- `extensions/feishu/src/card-action.ts` rejects blank callback tokens in the card-action lifecycle guard.
- `extensions/feishu/src/monitor.webhook-security.test.ts` covers missing-`encryptKey` startup and transport rejection.
- `extensions/feishu/src/monitor.card-action.lifecycle.test.ts` covers malformed blank-token card actions being dropped before handler dispatch.

Fix commit included in `v2026.4.15` and absent from `v2026.4.14`:

- `c8003f1b33ed2924be5f62131bd28742c5a41aae` via PR #66707

Thanks to @dhyabi2 for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-xh72-v6v9-mwhc
- https://nvd.nist.gov/vuln/detail/CVE-2026-44109
- https://github.com/openclaw/openclaw/pull/66707
- https://github.com/openclaw/openclaw/commit/c8003f1b33ed2924be5f62131bd28742c5a41aae
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-authentication-bypass-in-feishu-webhook-and-card-action-validation
