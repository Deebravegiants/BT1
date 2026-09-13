# [H] ZeptoClaw: Generic webhook channel trusts caller-supplied identity fields; allowlist is checked against untrusted payload data

## Summary
Severity: High
Advisory: GHSA-46q5-g3j9-wx5c
CVE: CVE-2026-32231
CWE: CWE-306, CWE-345
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-46q5-g3j9-wx5c
Type: github-advisory

## Affected
- crates.io: `zeptoclaw` — affected >=0 <0.7.6

## Details
### Summary
The generic webhook channel trusts caller-supplied identity fields (`sender`, `chat_id`) from the request body and applies authorization checks to those untrusted values. Because authentication is optional and defaults to disabled (`auth_token: None`), an attacker who can reach `POST /webhook` can spoof an allowlisted sender and choose arbitrary `chat_id` values, enabling high-risk message spoofing and potential IDOR-style session/chat routing abuse.

### Details
Relevant code paths:

- `src/channels/webhook.rs:121` sets runtime default `auth_token: None`.
- `src/config/types.rs:910` also defaults webhook config `auth_token` to `None`.
- `src/channels/webhook.rs:224` (`validate_auth`) explicitly allows requests when no token is configured.
- `src/channels/webhook.rs:128` defines `WebhookPayload` with identity fields fully controlled by caller input:
  - `sender: String`
  - `chat_id: String`
- `src/channels/webhook.rs:421` performs allowlist authorization using `payload.sender`.
- `src/channels/webhook.rs:433` and `src/channels/webhook.rs:434` create `InboundMessage` using untrusted `payload.sender` and `payload.chat_id`.

Why this is vulnerable:

- The system treats user-provided JSON identity as authoritative identity.
- Allowlist enforcement does not verify sender authenticity beyond that payload value.
- `chat_id` is also attacker-controlled, so routing/session association can be steered to arbitrary chats/conversations.
- If the webhook is exposed without strong upstream authn/authz controls, spoofing is straightforward.

### PoC
1. Configure the webhook channel in a vulnerable posture (common default behavior):
   - `enabled = true`
   - `bind_address = "0.0.0.0"` (or any reachable interface)
   - `port = 9876`
   - `path = "/webhook"`
   - `auth_token = null` (or omitted)
   - `allow_from = ["trusted-user-1"]`
   - `deny_by_default = true`
2. Start ZeptoClaw.
3. Send a forged request with attacker-chosen `sender` and `chat_id`, without any `Authorization` header:

```bash
curl -i -X POST "http://127.0.0.1:9876/webhook" \
  -H "Content-Type: application/json" \
  --data '{
    "message":"FORGED: run privileged workflow",
    "sender":"trusted-user-1",
    "chat_id":"victim-chat-42"
  }'
```

4. Observe:
   - Response is `HTTP/1.1 200 OK`.
   - Message is accepted as if it originated from `trusted-user-1`.
   - Message is routed under attacker-chosen `chat_id` (`victim-chat-42`).

### Impact
- Vulnerability type:
  - Authentication/authorization bypass (identity spoofing)
  - IDOR-style routing/control issue via attacker-chosen `chat_id`
- Affected deployments:
  - Any deployment exposing the generic webhook endpoint without strict upstream authentication and identity binding.
- Security consequences:
  - Forged inbound messages from spoofed trusted users.
  - Bypass of allowlist intent by injecting allowlisted sender IDs in payload.
  - Cross-chat/session contamination or hijacking by choosing arbitrary `chat_id`.
  - Potential unauthorized downstream agent/tool actions triggered by malicious input.

## References
- https://github.com/qhkm/zeptoclaw/security/advisories/GHSA-46q5-g3j9-wx5c
- https://nvd.nist.gov/vuln/detail/CVE-2026-32231
- https://github.com/qhkm/zeptoclaw/pull/324
- https://github.com/qhkm/zeptoclaw/commit/bf004a20d3687a0c1a9e052ec79536e30d6de134
- https://github.com/qhkm/zeptoclaw
- https://github.com/qhkm/zeptoclaw/releases/tag/v0.7.6
