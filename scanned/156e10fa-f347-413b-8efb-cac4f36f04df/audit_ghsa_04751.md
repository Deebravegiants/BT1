# [H] PraisonAI: Webhook signature verification skipped (fail-open) when secret unset, allowing forged inbound webhooks (WhatsApp & Linear bots)

## Summary
Severity: High
Advisory: GHSA-x92v-rpx6-p6cw
CVE: CVE-2026-57122
CWE: CWE-345, CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-x92v-rpx6-p6cw
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=0 <4.6.59

## Details
The WhatsApp and Linear bot adapters verify the inbound webhook HMAC signature only
when a secret is configured. When the secret environment variable is unset — the
default on a fresh install and common in development — verification is skipped entirely
and the webhook body is parsed and dispatched as a genuine, trusted event. A remote,
unauthenticated attacker who can reach the bot's webhook endpoint can inject arbitrary
platform events.

Affected code:

WhatsApp - src/praisonai/praisonai/bots/whatsapp.py
- __init__ (line 108): self._app_secret = app_secret or os.environ.get("WHATSAPP_APP_SECRET", "")  -> defaults to ""
- route (line 246): app.router.add_post(self._webhook_path, self._handle_webhook)  -> default path "/webhook"
- _handle_webhook (lines 585-595): `if self._app_secret:` gates the ENTIRE check; when falsy the body is
  json.loads()'d and dispatched to _process_webhook_data() with no verification.

Linear - src/praisonai/praisonai/bots/linear.py
- __init__ (line 86): self._signing_secret = signing_secret or os.environ.get("LINEAR_WEBHOOK_SECRET", "")  -> ""
- _handle_webhook (lines 244-248): same `if self._signing_secret:` fail-open guard.
- start() (lines 169-170): only logs a warning; does not fail closed.

The _verify_signature implementations themselves are correct (constant-time HMAC-SHA256);
the defect is that verification is bypassed when the secret is absent.

Impact:
- WhatsApp: attacker POSTs a crafted Meta Cloud API payload spoofing any sender and message
  text; injected into agent sessions and processed as a real user message (prompt injection,
  unauthorized agent/command invocation, contact impersonation).
- Linear: attacker POSTs forged AgentSession / Comment events, causing the agent to act on and
  comment on issues no legitimate event referenced.
The webhook routes require no other authentication, so exploitation needs only network
reachability.

Proof of concept (bot started without the secret - the default):

  curl -X POST http://VICTIM:PORT/webhook \
    -H 'Content-Type: application/json' \
    -d '{"object":"whatsapp_business_account","entry":[{"changes":[{"value":
         {"messages":[{"from":"15551234567","id":"wamid.x","type":"text",
         "text":{"body":"attacker-injected message"}}]}}]}]}'
  # No X-Hub-Signature-256 header; bot returns 200 and processes the message.
  # Linear: omit LINEAR_WEBHOOK_SECRET and POST without a Linear-Signature header.

A self-contained PoC that executes the real _handle_webhook / _verify_signature source
extracted from the repo confirms: secret unset -> status 200, payload dispatched (VULNERABLE);
secret set + no signature -> status 403, nothing dispatched (control).

Remediation:
Fail closed. When no secret is configured, reject all webhooks (HTTP 403) and refuse to start
the adapter unless a secret is set (or an explicit, clearly-named insecure-dev override is given):

  if not self._app_secret:
      return web.Response(status=403, text="Webhook secret not configured")
  signature = request.headers.get("X-Hub-Signature-256", "")
  if not self._verify_signature(body, signature):
      return web.Response(status=403, text="Invalid signature")

Distinct from prior advisories:
The accepted default-insecure advisories cover a different surface/mechanism — CALL_SERVER_TOKEN
unset (GHSA-86qc-r5v2-v6x6) and the JWT key default "dev-secret-change-me" (GHSA-3qg8-5g3r-79v5).
This is in the bot webhook adapters and the mechanism is skipping signature verification entirely
when the secret is absent, not a weak default key.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-x92v-rpx6-p6cw
- https://github.com/MervinPraison/PraisonAI
