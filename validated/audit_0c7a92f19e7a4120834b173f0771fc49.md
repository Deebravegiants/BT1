Audit Report

## Title
Unbounded `topics` array in Web API Trigger requests causes O(N×M) resource-exhaustion DoS during allowlist matching - (File: `core/capabilities/webapi/trigger/trigger.go`)

## Summary
`triggerConnectorHandler.processTrigger` iterates over every registered trigger and every entry of the attacker-supplied `payload.Topics` array without any upper bound, and this handler is invoked synchronously and in-line from `gatewayConnector.readLoop` for each message read from a Gateway connection. Because the Gateway's `HandleLegacyUserMessage` path explicitly has no sender allowlist ("TODO: apply allowlist and rate-limiting here") and forwards the request to every DON member node, an unprivileged external caller who can produce a syntactically valid signed message can pack a large number of short topic strings into a single request (bounded only by the HTTP body size limit) to inflate the cost of this loop and block further message processing on the connector's read loop.

## Finding Description
`processTrigger` only validates that `topics` is non-empty, then does a nested loop over `triggers × topics`, performing map lookups and rate-limiter calls under `h.mu`-protected trigger state for each iteration:
<cite repo="Alyssadaypin/chainlink--022" path="core/capabilities/webapi/trigger/trigger.go" start="91-119" />

`HandleGatewayMessage` decodes the request body into `TriggerRequestPayload` and calls `processTrigger` directly for `MethodWebAPITrigger`:
<cite repo="Alyssadaypin/chainlink--022" path="core/capabilities/webapi/trigger/trigger.go" start="167-200" />

On the Gateway side, `handler.HandleLegacyUserMessage` decodes the payload, validates only the `Timestamp` field and message staleness, and forwards to every DON member without any sender allowlist check — this is explicitly flagged as a TODO in the code:
<cite repo="Alyssadaypin/chainlink--022" path="core/services/gateway/handlers/capabilities/handler.go" start="384-419" />

The only size constraint on the request is `httpServer.handleRequest`'s `MaxRequestBytesLimiter`-bounded body read, which permits payloads up to the configured max (default `MaxRequestBytes`/`MaxMessageLenBytes`, hundreds of KB):
<cite repo="Alyssadaypin/chainlink--022" path="core/services/gateway/network/httpserver.go" start="211-224" />

Finally, the node's `gatewayConnector.readLoop` synchronously calls `handler.HandleGatewayMessage` for each inbound message before reading the next one from the connection, so a single expensive `processTrigger` call blocks subsequent message handling on that connection:
<cite repo="Alyssadaypin/chainlink--022" path="core/services/gateway/connector/connector.go" start="268-298" />

Since a `topics` entry can be a very short string (e.g., `"a"`), tens of thousands of entries can fit within the byte-size limit, producing a large `triggers × topics` loop even with just a handful of registered triggers. The existing checks (`Message.Validate`, `HandleLegacyUserMessage`'s timestamp/staleness check) validate message structure and freshness but do not bound array-typed payload fields like `Topics`.

## Impact Explanation
This is a resource-exhaustion / denial-of-service issue: an oversized `topics` array causes disproportionate CPU cost and blocks the connector's synchronous read loop, delaying delivery of legitimate trigger/target/compute messages over the same Gateway connection. It does not cause fund loss, authentication bypass, or data exposure, so it should be classified as availability-impacting rather than a critical/high-severity vulnerability. It matches the referenced "unbounded loop over user-supplied array" bug class and is a legitimate root cause finding rooted in application code rather than network/host-layer issues.

## Likelihood Explanation
No privileged role, valid node registration, or workflow ownership is required. As confirmed by `HandleLegacyUserMessage`, sender allowlisting is not yet implemented at the Gateway layer ("TODO: apply allowlist and rate-limiting here"), and the payload's `Topics` array size is never checked prior to node-side processing. Any external client capable of signing a message with a self-chosen ECDSA key and reaching the Gateway's HTTP endpoint can construct and repeatedly send such a request.

## Recommendation
Enforce a maximum length on `payload.Topics` (and `TriggerConfig.AllowedTopics`) before entering the nested loop in `processTrigger`, e.g., reject requests where `len(topics) > maxTopicsPerRequest`. Additionally, consider bounding array-typed payload fields generically at Gateway message validation time, implementing the still-outstanding sender allowlist/rate-limiting TODO in `handler.HandleLegacyUserMessage`, and moving expensive per-message handler work off the connector's synchronous `readLoop` so a single costly message cannot delay subsequent Gateway traffic.

## Proof of Concept
1. Construct a `web-api-trigger` JSON-RPC request whose `TriggerRequestPayload.Topics` contains tens of thousands of short strings (e.g., `"a0"`..`"a49999"`), staying under the configured `MaxRequestBytes`/`MaxMessageLenBytes`.
2. Sign the message body with an arbitrary, self-generated ECDSA key (`msg.Sign(privateKey)`) — no allowlisting or privileged role is required for this Gateway path.
3. Submit via the Gateway's HTTP endpoint; `Message.Validate()` only checks ID/Method/DonID/Receiver lengths and signature format, and `handler.HandleLegacyUserMessage` forwards to all DON members without a sender allowlist check.
4. On the node side, `gatewayConnector.readLoop` synchronously calls `triggerConnectorHandler.HandleGatewayMessage` → `processTrigger`, iterating `len(registeredWorkflows) × len(topics)` times while holding the trigger-state mutex briefly and calling into per-trigger rate limiters, delaying processing of subsequent messages on that connection. A Go benchmark/unit test invoking `processTrigger` directly with a large `topics` slice and several registered triggers would demonstrate the near-linear-in-input-size CPU cost with no upper bound enforced.