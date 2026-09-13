# [M] slack-go `SecretsVerifier` accepts empty signing secret without precondition

## Summary
Severity: Medium
Advisory: GHSA-gxhx-2686-5h9g
CWE: CWE-1391, CWE-287, CWE-326
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-gxhx-2686-5h9g
Type: github-advisory

## Affected
- Go: `github.com/slack-go/slack` — affected >=0 <0.23.1

## Details
`SecretsVerifier` in slack-go/slack before v0.23.1 accepts an empty signing secret without error. If an application is misconfigured (e.g., an unset or empty `SLACK_SIGNING_SECRET`), `NewSecretsVerifier` builds an HMAC-SHA256 keyed with an empty string, allowing an unauthenticated attacker to forge a valid `X-Slack-Signature` and bypass Slack request authentication. Fixed in v0.23.1, which rejects empty secrets with `ErrInvalidConfiguration`. This is patched in version 0.23.1.

## References
- https://github.com/slack-go/slack/security/advisories/GHSA-gxhx-2686-5h9g
- https://github.com/slack-go/slack/commit/34ad5c052e446f58505ae8d81a2a72821de107cc
- https://github.com/slack-go/slack
- https://github.com/slack-go/slack/releases/tag/v0.23.1
