# [H] OpenClaw Slack: dmPolicy=open allowed any DM sender to run privileged slash commands

## Summary
Severity: High
Advisory: GHSA-v773-r54f-q32w
CVE: CVE-2026-28392
CWE: CWE-285, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-v773-r54f-q32w
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
## Summary

When Slack DMs are configured with `dmPolicy=open`, the Slack slash-command handler incorrectly treated any DM sender as command-authorized. This allowed any Slack user who could DM the bot to execute privileged slash commands via DM, bypassing intended allowlist/access-group restrictions.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.13`
- Affected configuration: Slack DMs enabled with `channels.slack.dm.policy: open` (aka `dmPolicy=open`)

## Impact

Any Slack user in the workspace who can DM the bot could invoke privileged slash commands via DM.

## Fix

The slash-command path now computes `CommandAuthorized` for DMs using the same allowlist/access-group gating logic as other inbound paths.

Fix commit(s):
- f19eabee54c49e9a2e264b4965edf28a2f92e657

## Release Process Note

`patched_versions` is set to the planned next release (`2026.2.14`). Once that npm release is published, this advisory should be published.

Thanks @christos-eth for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-v773-r54f-q32w
- https://nvd.nist.gov/vuln/detail/CVE-2026-28392
- https://github.com/openclaw/openclaw/commit/f19eabee54c49e9a2e264b4965edf28a2f92e657
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
- https://www.vulncheck.com/advisories/openclaw-privilege-escalation-in-slack-slash-command-handler-via-direct-messages
