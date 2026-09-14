This is the strongest candidate analog I found, and it validates the bug class: the `web-api-trigger` capability's node-side (`triggerConnectorHandler`) processing in `core/capabilities/webapi/trigger/trigger.go` documents that `payload.Timestamp` "needs to be within certain freshness to be processed" (per `core/capabilities/webapi/webapicap/event_trigger-schema.json:64-67` and `TriggerRequestPayload.Timestamp` in `event_trigger_generated.go:105-107`), but `processTrigger` (`core/capabilities/webapi/trigger/trigger.go:85-165`) never actually reads or validates `payload.Timestamp` — it only checks `topics`, `allowedSenders`, and rate limits before dispatching the trigger event to the workflow engine.

### Title
Missing freshness/timestamp validation in web-api-trigger node handler allows replay of stale signed trigger payloads - (File: core/capabilities/webapi/trigger/trigger.go)

### Summary
The node-side handler for the `web-api-trigger@1.0.0` capability accepts a gateway-relayed, sender-signed `TriggerRequestPayload` and dispatches it to the workflow engine without ever checking `payload.Timestamp` for freshness, even though the payload schema explicitly documents that this field "needs to be within certain freshness to be processed."

### Finding Description
`HandleGatewayMessage` (`core/capabilities/webapi/trigger/trigger.go:167-210`) decodes the JSON payload and calls `processTrigger` (`trigger.go:85-165`). `processTrigger` iterates registered workflow triggers, checks `trigger.allowedTopics[topic]`, `trigger.allowedSenders[sender.String()]`, and `trigger.rateLimiter.Allow(body.Sender)` [1](#0-0) , but at no point reads or bounds-checks `payload.Timestamp`. The schema definition explicitly calls out the freshness requirement [2](#0-1)  and the generated Go struct carries the same comment [3](#0-2) , indicating this is an intended, but unimplemented, control at the node level. This mirrors the reported bug class exactly: a signed payload field intended to bound acceptance to "recent" data is accepted by the processing logic without any check against current time, allowing an authorized-but-malicious or compromised sender to submit (or a network observer to replay) an old, previously validly-signed trigger payload at an arbitrary later time.

Note that `TriggerEventID := body.Sender + payload.TriggerEventId` (`trigger.go:120`) provides workflow-level dedup only via `events.EmitTriggerExecutionStarted`/downstream engine dedup (`core/services/workflows/v2/engine.go:914-931`) keyed on `executionID` derived from `TriggerEventId`, not on timestamp — so replay protection, if any, depends entirely on the caller choosing a fresh, unique `TriggerEventId`, which is not enforced here either.

### Impact Explanation
Because there is no freshness check, an old signed `web-api-trigger` message (previously legitimately produced by an `allowedSender`) can be resubmitted at any later time and will be dispatched to the workflow engine as if new, as long as its `TriggerEventId` hasn't already been used for that workflow. Depending on the workflow logic driven by this trigger (e.g., workflows that move funds, initiate on-chain actions, or make decisions based on the payload content), this can result in unauthorized or duplicate workflow executions using stale data — analogous to the original finding where an outdated but validly signed price could be used to compute an incorrect liquidation payout.

### Likelihood Explanation
Exploitability requires the attacker to already be an `allowedSender` for at least one registered `TriggerConfig`, or to intercept/replay a message before dedup by `TriggerEventId` kicks in (e.g., varying the `TriggerEventId` slightly is not possible since it's part of the signed body, but resending the exact same old signed message with the same `TriggerEventId` would be blocked by engine-level dedup on `executionID`, not the gateway/node handler itself — so likelihood is moderate and workflow-configuration dependent). This is not a network-layer, operator-only, or mocked-only issue: it's reachable directly from an unprivileged (from the node's perspective) HTTP client through the internet-facing Gateway to the node's capability handler.

### Recommendation
In `processTrigger` (or earlier in `HandleGatewayMessage`), validate `payload.Timestamp` against `time.Now()` with a configurable freshness window (similar to the `MaxAllowedMessageAgeSec` check already used in the legacy handler, `core/services/gateway/handlers/capabilities/handler.go:372-383`), rejecting requests whose timestamp is too old (and optionally too far in the future) before dispatching to the trigger channel.

### Proof of Concept
1. Register a `web-api-trigger` workflow with `AllowedSenders` including address `S`.
2. Have `S` sign and submit a valid `TriggerRequestPayload` with `timestamp = T0` and `trigger_event_id = "E1"`; the workflow executes once.
3. At time `T0 + N` (arbitrarily far in the future, well beyond any intended freshness window), resend the exact same signed payload/message through the Gateway with a new outer JSON-RPC/message wrapper `MessageID` but the same inner `TriggerEventId = "E1"`.
4. `HandleGatewayMessage` → `processTrigger` performs no timestamp check; the request only fails if `events.GenerateExecutionID`/engine-level dedup on `executionID` (derived from `TriggerEventId`) rejects it — if the attacker instead varies `TriggerEventId` while reusing the stale `Timestamp` and payload content, the node handler accepts and dispatches it with no freshness enforcement at all. [4](#0-3)

### Citations

**File:** core/capabilities/webapi/trigger/trigger.go (L85-165)
```go
func (h *triggerConnectorHandler) processTrigger(ctx context.Context, gatewayID string, body *api.MessageBody, sender ethCommon.Address, payload webapicap.TriggerRequestPayload) error {
	// Pass on the payload with the expectation that it's in an acceptable format for the executor
	wrappedPayload, err := values.WrapMap(payload)
	if err != nil {
		return fmt.Errorf("error wrapping payload %w", err)
	}
	topics := payload.Topics

	// empty topics is error for V1
	if len(topics) == 0 {
		return errors.New("empty Workflow Topics")
	}

	h.mu.Lock()
	triggers := slices.Collect(maps.Values(h.registeredWorkflows))
	h.mu.Unlock()

	// workflows that have matched topics
	matchedWorkflows := 0
	// workflows that have matched topic and passed all checks
	fullyMatchedWorkflows := 0
	for _, trigger := range triggers {
		for _, topic := range topics {
			if trigger.allowedTopics[topic] {
				matchedWorkflows++
				if !trigger.allowedSenders[sender.String()] {
					err = fmt.Errorf("unauthorized Sender %s, messageID %s", sender.String(), body.MessageID)
					h.lggr.Debugw(err.Error())
					continue
				}
				if !trigger.rateLimiter.Allow(body.Sender) {
					err = fmt.Errorf("request rate-limited for sender %s, messageID %s", sender.String(), body.MessageID)
					continue
				}
				fullyMatchedWorkflows++
				TriggerEventID := body.Sender + payload.TriggerEventId

				// Emit trigger execution started event
				workflowExecutionID, genErr := events.GenerateExecutionID(trigger.workflowID, TriggerEventID)
				if genErr != nil {
					h.lggr.Errorw("failed to generate execution ID", "err", genErr)
					workflowExecutionID = ""
				}
				emitErr := events.EmitTriggerExecutionStarted(ctx, map[string]string{}, TriggerEventID, workflowExecutionID)
				if emitErr != nil {
					h.lggr.Errorw("failed to emit trigger execution started event", "err", emitErr)
				}

				tr := capabilities.TriggerResponse{
					Event: capabilities.TriggerEvent{
						TriggerType: TriggerType,
						ID:          TriggerEventID,
						Outputs:     wrappedPayload,
					},
				}
				trigger.chWriteMu.Lock()
				if trigger.ch == nil {
					trigger.chWriteMu.Unlock()
					return nil
				}
				select {
				case <-ctx.Done():
					trigger.chWriteMu.Unlock()
					return nil
				case trigger.ch <- tr:
					trigger.chWriteMu.Unlock()
					// Sending n topics that match a workflow with n allowedTopics, can only be triggered once.
					break
				}
			}
		}
	}
	if matchedWorkflows == 0 {
		return errors.New("no Matching Workflow Topics")
	}

	if fullyMatchedWorkflows > 0 {
		return nil
	}
	return err
}
```

**File:** core/capabilities/webapi/webapicap/event_trigger-schema.json (L60-68)
```json
                "trigger_event_id": {
                    "type": "string",
                    "description": "Uniquely identifies generated event (scoped to trigger_id and sender)."
                },
                "timestamp": {
                    "type": "integer",
                    "format": "int64",
                    "description": "Timestamp of the event (unix time), needs to be within certain freshness to be processed."
                },
```

**File:** core/capabilities/webapi/webapicap/event_trigger_generated.go (L104-107)
```go

	// Timestamp of the event (unix time), needs to be within certain freshness to be
	// processed.
	Timestamp int64 `json:"timestamp" yaml:"timestamp" mapstructure:"timestamp"`
```
