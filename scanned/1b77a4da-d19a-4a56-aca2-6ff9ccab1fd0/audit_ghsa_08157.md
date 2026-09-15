# [H] OpenClaw authorization bypass: operator.write can resolve exec approvals via chat.send -> /approve

## Summary
Severity: High
Advisory: GHSA-mqpw-46fh-299h
CVE: CVE-2026-28473
CWE: CWE-269, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-mqpw-46fh-299h
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.2

## Details
## Summary

### What this means (plain language)

If you give a client “chat/write” access to the gateway (`operator.write`) but you do not intend to let that client approve exec requests (`operator.approvals`), affected versions could still let that client approve/deny a pending exec approval by sending the `/approve` chat command.

This is mainly relevant for shared or multi-client setups where different tokens are intentionally scoped differently. Single-operator installs are typically less impacted.

### Technical summary

A gateway client authenticated with a device token scoped only to `operator.write` (without `operator.approvals`) could approve/deny pending exec approval requests by sending a chat message containing the built-in `/approve` command.

`exec.approval.resolve` is correctly scoped to `operator.approvals` for direct RPC calls, but the `/approve` command path invoked it via an internal privileged gateway client.

## Affected Packages / Versions

- `openclaw` (npm): `< 2026.2.2`

## Fix

- Fixed in `openclaw` `2026.2.2`.
- Fix commit(s): `efe2a464afcff55bb5a95b959e6bd9ec0fef086e`.
- Change: when `/approve` is invoked from gateway clients (webchat/internal channel), it now requires the requesting client to have `operator.approvals` (or `operator.admin`).

## Workarounds

- Upgrade to `openclaw >= 2026.2.2`.
- If you cannot upgrade: avoid issuing write-only device tokens to untrusted clients; disable text commands (`commands.text=false`) or restrict access to the webchat/control UI.

## References

- Fix: `src/auto-reply/reply/commands-approve.ts`
- Coverage: `src/auto-reply/reply/commands-approve.test.ts`

## Release Process Note

This advisory is kept in draft; once the fixed npm versions are available, it can be published without further edits.

Thanks @yueyueL for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-mqpw-46fh-299h
- https://nvd.nist.gov/vuln/detail/CVE-2026-28473
- https://github.com/openclaw/openclaw/commit/efe2a464afcff55bb5a95b959e6bd9ec0fef086e
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-via-approve-chat-command
