# [M] OpenClaw: Non-owner command-authorized sender can change the owner-only `/send` session delivery policy

## Summary
Severity: Medium
Advisory: GHSA-39mp-545q-w789
CVE: CVE-2026-35620
CWE: CWE-285, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-39mp-545q-w789
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.24

## Details
> Fixed in OpenClaw 2026.3.24, the current shipping release.

**Title**  
Non-owner command-authorized sender can change the owner-only `/send` session delivery policy

**CWE**  
CWE-285 Improper Authorization

**CVSS v3.1**  
CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L  
Base score: **5.4 (Medium)**

**Severity Assessment**  
Medium. This is a real owner-only authorization bypass, but the demonstrated impact is limited to persistent mutation of the current session’s delivery policy rather than direct code execution, sandbox escape, or cross-host compromise.

**Impact**  
A non-owner sender who is allowed to run commands can invoke `/send on|off|inherit` and persistently change the current session’s `sendPolicy`, even though OpenClaw documents `/send` as owner-only.

That lets a lower-trust participant:
- disable reply delivery for the current session (`/send off`), suppressing future replies in that chat;
- re-enable reply delivery (`/send on`) after the owner intentionally disabled it;
- remove the session override (`/send inherit`).

**Affected Component**  
Verified against the latest published GitHub release tag `v2026.3.23` (`ccfeecb6887cd97937e33a71877ad512741e82b2`), published `2026-03-23T23:15:50Z`.

Exact vulnerable path on the shipped tag:
- `src/auto-reply/reply/commands-session.ts:212-239`
  - `handleSendPolicyCommand(...)` checks only `params.command.isAuthorizedSender`.
  - when true, it mutates `params.sessionEntry.sendPolicy` and persists the session entry.

Authorization behavior that makes this reachable:
- `src/auto-reply/command-auth.ts:401-407`
  - `senderIsOwner` is computed separately from general command authorization.
- `src/auto-reply/command-auth.ts:420-429`
  - command authorization can succeed even when `senderIsOwner === false`.
- `src/auto-reply/command-auth.owner-default.test.ts:10-47`
  - existing coverage confirms a sender can be command-authorized while not treated as owner.

Documented owner-only contract:
- `docs/tools/slash-commands.md:112`
  - `/send on|off|inherit` is documented as owner-only.
- `docs/concepts/session-tool.md:156`
  - `sendPolicy` is documented as settable via `sessions.patch` or owner-only `/send on|off|inherit`.

Related privilege model:
- `src/gateway/method-scopes.ts:131-133`
  - `sessions.patch` is admin-scoped, which reinforces that session-delivery-policy mutation is treated as privileged state.

Version history:
- The vulnerable handler exists in release history going back at least to commit `ea018a68ccb92dbc735bc1df9880d5c95c63ca35` (`refactor(auto-reply): split reply pipeline`).
- Earliest released affected tag found: `v2026.1.14-1`
- Latest released affected tag verified: `v2026.3.23`

**Technical Reproduction**  
1. Check out the shipped release tag `v2026.3.23`.
2. Configure a channel where:
   - a non-owner sender is allowed to run commands, for example through `commands.allowFrom`;
   - the owner identity is distinct, for example via `commands.ownerAllowFrom`.
3. Start or reuse a session with a live `sessionEntry` and `sessionStore`.
4. Send `/send off` as the non-owner but command-authorized sender.
5. Confirm the resolved command context has:
   - `isAuthorizedSender === true`
   - `senderIsOwner === false`
6. Observe that the handler still accepts the command, mutates `sessionEntry.sendPolicy`, and persists the session entry.

**Demonstrated Impact**  
The vulnerable handler performs a real persistent session-state change:
- `src/auto-reply/reply/commands-session.ts:232-238`
  - `/send inherit` deletes `sessionEntry.sendPolicy`
  - other modes assign `sessionEntry.sendPolicy = sendPolicyCommand.mode`
  - the handler then calls `persistSessionEntry(params)`

The mutation is not gated by owner status, only by general command authorization.

That changes subsequent delivery behavior for the current session, which matches the documented meaning of `sendPolicy`.

**Environment**  
- Product: OpenClaw
- Verified shipped tag: `v2026.3.23`
- Shipped tag commit: `ccfeecb6887cd97937e33a71877ad512741e82b2`
- Published GitHub release time: `2026-03-23T23:15:50Z`
- Verification date: `2026-03-24`

**Duplicate Check**  
Upon inspection there is no preexisting GHSA for `/send`.

This is distinct from:
- `GHSA-r7vr-gr74-94p8`
  - that advisory covered owner-only authorization bypasses for `/config` and `/debug`, not `/send`.

This is the same authorization class, but a different privileged command surface that still lacks the owner check.

**In Scope Check**  
This report is in scope under `SECURITY.md` because:
- it does **not** rely on adversarial operators sharing one gateway host or config;
- it does **not** rely on trusted local state tampering;
- `SECURITY.md:151-152` explicitly says non-owner sender status matters for owner-only tools and commands;
- `/send` is explicitly documented as owner-only, so this is a direct owner-only authorization bypass, not a complaint about normal shared-agent steering.

This is therefore a concrete authorization flaw against a documented product boundary.

**Remediation Advice**  
1. Change `/send` to require owner status, not just command authorization.
2. Reuse the same owner-only rejection pattern already used by privileged command surfaces such as `/config`, `/debug`, and owner-only `/plugins` writes.
3. Add regression coverage for the exact case where:
   - a non-owner sender is command-authorized;
   - `/send` must still be rejected unless `senderIsOwner === true`.
4. Verify that the owner can still use `/send on|off|inherit` normally.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-39mp-545q-w789
- https://github.com/openclaw/openclaw/security/advisories/GHSA-vqvg-86cc-cg83
- https://nvd.nist.gov/vuln/detail/CVE-2026-35620
- https://github.com/openclaw/openclaw/commit/555b2578a8cc6e1b93f717496935ead97bfbed8b
- https://github.com/openclaw/openclaw/commit/ccfeecb6887cd97937e33a71877ad512741e82b2
- https://github.com/openclaw/openclaw/commit/ea018a68ccb92dbc735bc1df9880d5c95c63ca35
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-missing-authorization-in-send-and-allowlist-chat-commands
