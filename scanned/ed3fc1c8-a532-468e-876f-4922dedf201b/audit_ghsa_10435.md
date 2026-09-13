# [H] Paperclip: codex_local inherited ChatGPT/OpenAI-connected Gmail and was able to send real email

## Summary
Severity: High
Advisory: GHSA-gqqj-85qm-8qhf
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-gqqj-85qm-8qhf
Type: github-advisory

## Affected
- npm: `paperclipai` — affected >=0

## Details
### Summary

A Paperclip-managed `codex_local` runtime was able to access and use a Gmail connector that I had connected in the ChatGPT/OpenAI apps UI, even though I had not explicitly connected Gmail inside Paperclip or separately inside Codex.

In my environment this enabled mailbox access and a real outbound email to be sent from my Gmail account. After I manually intervened to stop the workflow, follow-up retraction messages were also sent, confirming repeated outward write/send capability.

This appears to be a trust-boundary failure between Paperclip-managed Codex execution and inherited OpenAI app connectors, amplified by dangerous-by-default runtime settings.

### Details

Successful runtime calls include:

- `mcp__codex_apps__gmail_get_profile`
- `mcp__codex_apps__gmail_search_emails`
- `mcp__codex_apps__gmail_send_email`

The connected Gmail profile resolved to my personal account.

Inside the Paperclip-managed `codex-home`, I also found cached OpenAI curated connector state for Gmail under a path like:

- `codex-home/plugins/cache/openai-curated/gmail/.../.app.json`

This strongly suggests that the runtime had access to an already connected OpenAI apps surface rather than a Paperclip-specific Gmail integration that I intentionally configured.

Separately, in the installed Paperclip code, `codex_local` defaults `dangerouslyBypassApprovalsAndSandbox` to `true`, and the server-side agent creation path applies that default when the flag is omitted. In practice, that makes this boundary failure much more dangerous because a newly created `codex_local` agent can operate with approvals and sandbox bypassed by default.

The key issue is this: I had connected Gmail only in the ChatGPT/OpenAI apps UI. I had not intentionally connected Gmail inside Paperclip or separately inside Codex. Despite that, the Paperclip-managed `codex_local` runtime was able to use Gmail read/write actions.

### PoC

Environment:

- self-hosted Paperclip instance using `codex_local`
- Gmail connected in the ChatGPT/OpenAI apps UI
- no explicit Gmail connection configured inside Paperclip for this test
- `codex_local` agent created and run with default behavior

Observed reproduction path:

1. Connect Gmail in the ChatGPT/OpenAI apps UI.
2. Create or run a Paperclip `codex_local` agent.
3. Execute a task that inspects mailbox state or performs outward communication.
4. Observe successful Gmail connector calls such as:
   - `mcp__codex_apps__gmail_get_profile`
   - `mcp__codex_apps__gmail_search_emails`
   - `mcp__codex_apps__gmail_send_email`
5. Observe that the connected profile resolves to the ChatGPT/OpenAI-connected Gmail account and that mailbox reads and real sends are possible.

Private evidence available on request:

- successful `get_profile` / `search` / `send` logs
- Paperclip-managed `codex-home` Gmail connector cache path(s)
- screenshot showing Gmail write-capable actions such as `send_email`, `send_draft`, and `update_draft` exposed in the connected-app UI
- incident timeline showing that a real outbound email was sent
- recipient organizations, timestamps, message IDs, and sanitized evidence for both the original outbound email and the subsequent retraction messages

### Impact

This was not only theoretical in my environment. It resulted in:

- mailbox identity disclosure
- mailbox search / thread access
- a real outbound email being sent from a personal connected Gmail account to an external third party
- follow-up retraction messages being sent after manual intervention, confirming repeated outward write/send capability

From an operator/security perspective, connecting Gmail in the ChatGPT/OpenAI apps UI should not automatically make that connector available to a Paperclip-managed local agent runtime, especially not for write/send actions.

One or more of the following:

- no inherited OpenAI app connectors by default in Paperclip-managed `codex_local` runs
- send/write connectors blocked by default
- explicit Paperclip-side opt-in before outward actions
- auditable approval and provenance for connector-mediated actions
- safer defaults, including `dangerouslyBypassApprovalsAndSandbox = false`

## References
- https://github.com/paperclipai/paperclip/security/advisories/GHSA-gqqj-85qm-8qhf
- https://github.com/paperclipai/paperclip
