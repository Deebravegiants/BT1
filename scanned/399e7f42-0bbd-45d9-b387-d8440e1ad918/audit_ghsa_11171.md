# [H] OpneClaw accepts unsanitized iMessage attachment paths which allowed SCP remote-path command injection

## Summary
Severity: High
Advisory: GHSA-g2f6-pwvx-r275
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-g2f6-pwvx-r275
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.13

## Details
### Summary
`openclaw` versions `<= 2026.3.12` accepted unsanitized iMessage remote attachment paths when staging files over SCP, allowing shell metacharacters in the remote path operand.

### Affected Packages / Versions
- Package: `openclaw` (`npm`)
- Affected versions: `<= 2026.3.12`
- Fixed version: `2026.3.13`

### Details
The vulnerable path was the remote attachment staging flow in `src/auto-reply/reply/stage-sandbox-media.ts`. When `ctx.MediaRemoteHost` was set, OpenClaw staged the attachment by spawning `/usr/bin/scp` against `<remoteHost>:<remotePath>`. In affected releases, the remote host was normalized but the remote attachment path was not validated for shell metacharacters before being passed to the SCP remote operand. A sender-controlled iMessage attachment filename containing shell metacharacters could therefore trigger command execution on the configured remote host when remote attachment staging was enabled.

This issue is in scope under OpenClaw's trust model because it crosses an inbound content boundary into host command execution on a configured remote attachment host.

### Fix
`openclaw@2026.3.13` validates the SCP remote path before spawning `scp`. Current code calls `normalizeScpRemotePath(...)` and rejects paths containing shell metacharacters instead of passing them through to the remote shell.

Regression coverage exists in `src/auto-reply/reply.stage-sandbox-media.scp-remote-path.test.ts` (`rejects remote attachment filenames with shell metacharacters before spawning scp`).

### Fix Commit(s)
- `a54bf71b4c0cbe554a84340b773df37ee8e959de`

Thanks @lintsinghua for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-g2f6-pwvx-r275
- https://github.com/openclaw/openclaw/commit/a54bf71b4c0cbe554a84340b773df37ee8e959de
- https://github.com/openclaw/openclaw
