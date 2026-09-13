# [H] PraisonAI LinearBot processes unsigned webhooks when LINEAR_WEBHOOK_SECRET is missing

## Summary
Severity: High
Advisory: GHSA-fc26-m9pf-v56q
CVE: CVE-2026-56837
CWE: CWE-287, CWE-306, CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-fc26-m9pf-v56q
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=4.6.56 <4.6.59

## Details
# PraisonAI LinearBot processes unsigned webhooks when `LINEAR_WEBHOOK_SECRET` is missing

## Summary

PraisonAI's LinearBot starts a public webhook listener on `0.0.0.0` and treats
`LINEAR_WEBHOOK_SECRET` as optional. When the secret is absent, startup only logs
a warning and `_handle_webhook()` skips `Linear-Signature` verification entirely.

An unauthenticated network caller who can reach the webhook endpoint can submit
a forged `Linear-Event: AgentSession` request. The forged request is parsed,
scheduled for background processing, dispatched to `_handle_agent_session()`,
and passed into `BotSessionManager.chat()`. The bot then attempts to post the
agent response back to Linear under the configured bot token.

The local PoV is offline and deterministic. It does not contact Linear. It calls
the webhook handler directly, monkey-patches the outbound Linear comment path,
and proves both sides of the boundary:

- no secret configured: unsigned forged webhook returns `200`, invokes the
  agent session path once, and attempts one Linear comment;
- secret configured: missing and bad signatures both return `401` and do not
  invoke the agent;
- secret configured with valid HMAC: request returns `200` and invokes the
  agent, proving the control path still works.

## Affected Product

- Repository: `MervinPraison/PraisonAI`
- Package: `praisonai`
- Components:
  - `src/praisonai/praisonai/bots/linear.py`
  - `src/praisonai/praisonai/cli/features/bots_cli.py`

Validated affected:

- live `main` / latest observed release `v4.6.58`:
  `1ad58ca02975ff1398efeda694ea2ab78f20cf3e`
- previous local current checkout:
  `2f9677abb2ea68eab864ee8b6a828fd0141612e1`
- `v4.6.57`
- `v4.6.56`
- `v4.5.50`

Sampled tags where the LinearBot component was not present:

- `v4.5.49`
- `v4.5.51`
- `v4.6.9`
- `v4.6.10`

Suggested affected range: LinearBot-bearing releases with the fail-open
signature behavior, at least `4.5.50` and `>= 4.6.56, <= 4.6.58`. The
component appears non-contiguously in sampled tags, so maintainers should
confirm the exact packaged version history before publishing a final range.

## Root Cause

`LinearBot.__init__()` accepts an empty signing secret and falls back to an
empty environment value:

```python
self._signing_secret = signing_secret or os.environ.get("LINEAR_WEBHOOK_SECRET", "")
```

`start()` treats the missing secret as a warning instead of refusing to expose
the webhook listener:

```python
if not self._signing_secret:
    logger.warning("LINEAR_WEBHOOK_SECRET not set - webhook signatures will not be verified")

self._site = web.TCPSite(self._runner, "0.0.0.0", self._webhook_port)
```

`_handle_webhook()` only verifies the request if the secret is truthy:

```python
if self._signing_secret:
    signature = request.headers.get("Linear-Signature", "")
    if not self._verify_signature(raw_body, signature):
        return web.Response(status=401, text="Invalid signature")
```

With no secret configured, the code continues to JSON parsing, accepts a caller
supplied `webhookTimestamp`, reads the caller supplied `Linear-Event` header,
and schedules processing:

```python
event_type = request.headers.get("Linear-Event", "")
task = asyncio.create_task(self._process_webhook(event_type, body))
return web.Response(status=200, text="OK")
```

For `AgentSession`, the forged body is routed to the agent:

```python
if event_type == "AgentSession":
    await self._handle_agent_session(body)
...
response = await self._session_mgr.chat(self._agent, user_id, message.content)
await self._send_comment(...)
```

The CLI has the same fail-open posture: `start_linear()` loads
`LINEAR_WEBHOOK_SECRET`, prints a warning when it is missing, then reports a
public `http://0.0.0.0:<port>/webhook` endpoint with verification disabled.

## Why This Is Not Intended Behavior

PraisonAI's Linear Bot documentation tells operators to set
`LINEAR_WEBHOOK_SECRET`, pass it to `praisonai bot linear`, copy the Linear
webhook signing secret, and use it for HMAC-SHA256 verification. The same page
says missing secrets disable signature verification, while its best-practices
section says webhook secrets ensure authenticity.

Linear's webhook documentation says receivers should ensure requests were sent
by Linear by verifying the `Linear-Signature` HMAC over the raw body, then
checking that `webhookTimestamp` is recent. The timestamp check alone is not an
authentication boundary because an attacker can supply a current timestamp in a
forged body.

The implementation itself also confirms the intended boundary: when a secret is
configured, missing and bad signatures are rejected before agent dispatch. The
bug is the missing-secret fail-open mode on a public webhook server, not the
signature algorithm.

## Local PoV

Run against the latest observed release checkout:

```bash
python3 submission-bundle/praisonai-prai-cand-013-linear-webhook-signature-fail-open/poc/pov_prai_cand_013_linear_webhook_signature_fail_open.py --repo artifacts/repos/praisonai-v4.6.58
```

Expected output includes:

```json
{
  "candidate": "PRAI-CAND-013",
  "ok": true,
  "cases": {
    "no_secret_unsigned_forged_webhook": {
      "http_status": 200,
      "signing_secret_configured": false,
      "session_calls": [
        {
          "user_id": "linear-system",
          "content": "Issue: Forged Linear AgentSession event\n\nPRAI-CAND-013 local forged webhook payload"
        }
      ],
      "sent_comments": [
        {
          "issue_id": "issue-prai-cand-013",
          "comment": "agent response",
          "session_id": "prai-cand-013-session"
        }
      ]
    },
    "secret_missing_signature_control": {
      "http_status": 401,
      "session_calls": []
    },
    "secret_bad_signature_control": {
      "http_status": 401,
      "session_calls": []
    },
    "secret_valid_signature_control": {
      "http_status": 200,
      "session_calls": [
        {
          "user_id": "linear-system"
        }
      ]
    }
  }
}
```

Stored evidence:

- `evidence/pov-v4.6.58.json`
- `evidence/pov-live-main-v4.6.58.json`
- `evidence/pov-current-head.json`
- `evidence/version-sweep.tsv`

## Impact

If a PraisonAI operator starts LinearBot with a Linear token but omits
`LINEAR_WEBHOOK_SECRET`, any network caller that can reach the webhook endpoint
can spoof Linear webhook events and invoke the configured agent through the
Linear integration.

For the `AgentSession` event path, this lets the attacker supply issue title and
description content that becomes the agent input. Depending on the configured
agent and tools, this can cause unauthorized LLM/tool execution, consume paid
model quota, create or update Linear comments under the bot identity, and drive
the bot into workflows intended only for authenticated Linear events.

This report does not claim arbitrary code execution by default. The concrete
boundary crossed is unauthenticated remote agent invocation through a forged
Linear webhook.

## Suggested Fix

Fail closed for public webhook listeners:

1. Refuse to start LinearBot when `LINEAR_WEBHOOK_SECRET` is missing, unless an
   explicit development-only option such as
   `--insecure-skip-webhook-signature-verification` is provided.
2. In `_handle_webhook()`, reject requests when no signing secret is configured
   instead of silently skipping verification.
3. Preserve raw-body HMAC verification and constant-time comparison for the
   configured-secret path.
4. Treat timestamp freshness as replay protection after signature validation,
   not as a replacement for authentication.
5. Prefer loopback binding by default, or require an explicit host flag for
   public binding.
6. Add regression tests:
   - no signing secret rejects startup or rejects webhook requests;
   - missing signature with a configured secret returns `401`;
   - invalid signature with a configured secret returns `401`;
   - valid HMAC with a configured secret returns success;
   - stale timestamp after valid HMAC returns `401`;
   - the CLI does not advertise a public unauthenticated webhook by default.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-fc26-m9pf-v56q
- https://github.com/MervinPraison/PraisonAI
