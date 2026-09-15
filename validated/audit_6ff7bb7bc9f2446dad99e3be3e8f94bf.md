This confirms `donConfig` (the fan-out target set + static `F`) is loaded once from the job spec at handler construction (`config.DONConfig{DonID, F, Members}` via `shardedDONsToLegacy` / `newHandlerWithAuthorizer`) and is never updated from the live capabilities registry, while `donForVaultCapability` in the aggregator independently queries the live registry on every `Aggregate` call. These are two genuinely separate data sources, so the claim that they can diverge after a registry reconfiguration is structurally accurate based on the code as written.Audit Report

## Title
Vault gateway aggregator recomputes DON quorum/threshold from the live capabilities registry instead of the DON snapshot the request was sent to, permanently stalling in-flight requests after a DON reconfiguration - (File: `core/services/gateway/handlers/vault/aggregator.go`)

## Summary
The gateway's Vault handler fans a request out to a fixed set of nodes captured at job-config time (`h.donConfig.Members`), but on every incoming node response the aggregator's `Aggregate` re-fetches the "current" vault DON from the live capabilities registry via `donForVaultCapability` and recomputes the quorum/signature threshold from that fresh snapshot rather than the DON addressed at fan-out time. `h.donConfig` is a static struct (`DonID`, `F`, `Members`) loaded once from the job spec, while the aggregator's DON lookup is a fully independent, live query — these two sources are not kept in sync anywhere in the reviewed code.

## Finding Description
`fanOutToVaultNodes` sends to `h.donConfig.Members`, a static snapshot built once at handler construction (`shardedDONsToLegacy` / `newHandlerWithAuthorizer`) from job-spec TOML, never updated afterward. [1](#0-0) [2](#0-1) 

`HandleNodeMessage` calls `h.aggregator.Aggregate` for every arriving node response, and `Aggregate` independently resolves the DON via `donForVaultCapability`, which queries the live `capabilitiesRegistry.DONsForCapability`, not the DON snapshot the request was originally sent to. [3](#0-2) [4](#0-3) 

Both the signature path (`int(don.F+1)` valid signatures against the current signer set) and the quorum fallback (`2*don.F+1` matching responses) derive their acceptance threshold from this freshly-resolved DON. [5](#0-4) [6](#0-5) 

If the registry's vault DON membership/`F` changes while a request is in flight, responses from the (now stale) `donConfig.Members` set can never satisfy the new threshold, and the request will eventually be reaped by `removeExpiredRequests` with `RequestTimeoutError`. [7](#0-6) 

No mechanism in the reviewed code binds an in-flight request/`activeRequest` to the DON snapshot valid at fan-out time; `activeRequest` only stores `req`, `responses`, and `createdAt`. [8](#0-7) 

This is a real, reachable code-path bug: `h.donConfig` is genuinely static (set once from job spec at construction and never refreshed), while `baseAggregator.donForVaultCapability` genuinely queries the live registry on every `Aggregate` call — confirmed by direct code inspection with no synchronization mechanism found between the two.

## Impact Explanation
Any legitimate, unprivileged user's in-flight vault request (secrets create/update/delete/list) can be permanently stalled and time out if the vault DON's membership or `F` changes in the capabilities registry while the request is outstanding. This is a denial-of-service against normal user requests, not requiring any attacker action — it is triggered by ordinary DON operational reconfiguration events. The user experiences a failed/timed-out request rather than corruption, unauthorized state change, or fund loss; the finding maps to a service-availability/reliability degradation for legitimate flows rather than an authentication bypass, key exfiltration, or unauthorized fund movement.

## Likelihood Explanation
Requires no attacker-controlled input — it is triggered purely by an operational event (DON reconfiguration via the capabilities registry) that must occur while at least one vault request is genuinely in flight and not yet aggregated. This is a normal/expected operational occurrence in a live CRE deployment (node onboarding/offboarding, fault-tolerance parameter changes), making the race window realistic though narrow (bounded by request round-trip time vs. reconfiguration propagation time). The root cause and mechanism are confirmed in code; likelihood of actual occurrence in production depends on how frequently DON reconfigurations coincide with in-flight requests, which cannot be fully quantified from static code review alone.

## Recommendation
Capture and pin the DON snapshot (membership + `F`) used at fan-out time on the `activeRequest`, and have `Aggregate` / `validateUsingSignatures` / `validateUsingQuorum` use that pinned snapshot for the lifetime of a given request instead of re-resolving the current registry DON on each incoming response. Alternatively, ensure `h.donConfig` and the aggregator's registry-derived DON are always kept in lockstep (e.g., both refresh atomically together), or explicitly detect and fail/reroute requests when the DON changes mid-flight rather than allowing silent timeout.

## Proof of Concept
1. Construct a `handler` with `donConfig.Members = {N1..N4}`, static and never refreshed after construction (`core/services/gateway/handler_factory.go` `shardedDONsToLegacy`).
2. Fire `HandleJSONRPCUserMessage` for `secrets/create`, which calls `fanOutToVaultNodes`, sending to N1–N4 only.
3. Mock `capabilitiesRegistry.DONsForCapability` to return DON `{N1..N4, F=1}` initially, then switch to return `{N1..N6, F=2}` before all 4 responses arrive.
4. Feed 4 matching node responses from N1–N4 into `HandleNodeMessage`; assert that `Aggregate`/`validateUsingQuorum` requires `2*2+1=5` responses (from the new DON) which the 4 available responses can never satisfy, and observe the request eventually times out via `removeExpiredRequests` with `api.RequestTimeoutError`, despite N1–N4 satisfying the original `2*1+1=3` threshold.
5. This can be implemented as a Go unit test against `baseAggregator.Aggregate` with a mock `capabilitiesRegistry` returning different DON snapshots on successive calls, and a handler-level integration test asserting the terminal `RequestTimeoutError` despite quorum-sufficient original-committee responses.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L83-90)
```go
type activeRequest struct {
	req       jsonrpc.Request[json.RawMessage]
	responses map[string]*jsonrpc.Response[json.RawMessage]
	mu        sync.Mutex

	createdAt time.Time
	gwhandlers.Callback
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L360-384)
```go
// removeExpiredRequests removes expired requests from the pending requests map
func (h *handler) removeExpiredRequests(ctx context.Context) {
	h.mu.RLock()
	var expiredRequests []*activeRequest
	now := h.clock.Now()
	for _, userRequest := range h.activeRequests {
		if now.Sub(userRequest.createdAt) > h.requestTimeout {
			expiredRequests = append(expiredRequests, userRequest)
		}
	}
	h.mu.RUnlock()

	for _, er := range expiredRequests {
		responses := er.copiedResponses()
		var nodeResponses strings.Builder
		for nodeKey, nodeResponse := range responses {
			_, _ = fmt.Fprintf(&nodeResponses, "%s ---::: %v               ", nodeKey, nodeResponse)
		}
		nodeResponsesStr := nodeResponses.String()
		err := h.sendResponse(ctx, er, h.errorResponse(er.req, api.RequestTimeoutError, errors.New("request expired without getting quorum of responses from nodes. Available responses: "+nodeResponsesStr), []byte(nodeResponsesStr)))
		if err != nil {
			h.lggr.Errorw("error sending response to user", "requestID", er.req.ID, "error", err)
		}
	}
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L509-524)
```go
	ok := ar.addResponseForNode(nodeAddr, resp)
	if !ok {
		l.Errorw("duplicate response from node, ignoring", "nodeAddr", nodeAddr)
		return nil
	}

	copiedResponses := ar.copiedResponses()
	resp, err := h.aggregator.Aggregate(ctx, l, ar.req.ID, copiedResponses, resp)
	switch {
	case errors.Is(err, errInsufficientResponsesForQuorum):
		l.Debugw("aggregating responses, waiting for other nodes...", "error", err)
		return nil
	case err != nil:
		l.Error("quorum unobtainable, returning response to user...", "error", err, "responses", maps.Values(copiedResponses))
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.FatalError, err, nil))
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L736-744)
```go
func (h *handler) fanOutToVaultNodes(ctx context.Context, l logger.Logger, ar *activeRequest) error {
	var nodeErrors []error
	for _, node := range h.donConfig.Members {
		err := h.don.SendToNode(ctx, node.Address, &ar.req)
		if err != nil {
			nodeErrors = append(nodeErrors, err)
			l.Errorw("error sending request to node", "node", node.Address, "error", err)
		}
	}
```

**File:** core/services/gateway/handler_factory.go (L97-107)
```go
func shardedDONsToLegacy(shardedDON config.ShardedDONConfig) *config.DONConfig {
	var members []config.NodeConfig
	if len(shardedDON.Shards) > 0 {
		members = shardedDON.Shards[0].Nodes
	}
	return &config.DONConfig{
		DonID:   shardedDON.DonName,
		F:       shardedDON.F,
		Members: members,
	}
}
```

**File:** core/services/gateway/handlers/vault/aggregator.go (L55-89)
```go
func (a *baseAggregator) Aggregate(ctx context.Context, l logger.Logger, requestID string, resps map[string]jsonrpc.Response[json.RawMessage], currResp *jsonrpc.Response[json.RawMessage]) (*jsonrpc.Response[json.RawMessage], error) {
	don, err := a.donForVaultCapability(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to get DON for vault capability: %w", err)
	}

	if methodSupportsSignedOCRValidation(currResp.Method) {
		currResp, err = a.validateUsingSignatures(ctx, l, don.DON, don.Nodes, requestID, currResp)
		if err == nil {
			return currResp, nil
		}

		l.Debugw("failed to validate signatures, falling back to quorum aggregation", "error", err)
	}

	currResp, err = a.validateUsingQuorum(don.DON, resps, l)
	if err != nil {
		return nil, fmt.Errorf("failed to validate using quorum: %w", err)
	}

	return currResp, nil
}

func (a *baseAggregator) donForVaultCapability(ctx context.Context) (*capabilities.DONWithNodes, error) {
	dons, err := a.capabilitiesRegistry.DONsForCapability(ctx, vaultcommon.CapabilityID)
	if err != nil {
		return nil, err
	}
	if len(dons) == 0 {
		return nil, fmt.Errorf("no DON found for vault capability %s", vaultcommon.CapabilityID)
	}
	if len(dons) == 1 {
		don := dons[0]
		return &don, nil
	}
```

**File:** core/services/gateway/handlers/vault/aggregator.go (L136-141)
```go
func (a *baseAggregator) validateUsingQuorum(don capabilities.DON, resps map[string]jsonrpc.Response[json.RawMessage], l logger.Logger) (*jsonrpc.Response[json.RawMessage], error) {
	requiredQuorum := int(2*don.F + 1)

	if len(resps) < requiredQuorum {
		return nil, errInsufficientResponsesForQuorum
	}
```

**File:** core/services/gateway/handlers/vault/aggregator.go (L243-265)
```go
func (a *baseAggregator) validateUsingSignatures(ctx context.Context, l logger.Logger, don capabilities.DON, nodes []capabilities.Node, requestID string, resp *jsonrpc.Response[json.RawMessage]) (*jsonrpc.Response[json.RawMessage], error) {
	if resp.Result == nil {
		if resp.Error != nil {
			return nil, errors.New("response has an error, cannot validate signatures. Error: " + resp.Error.Error())
		}
		return nil, errors.New("response result and error both are is nil: cannot validate signatures")
	}

	r := &vaulttypes.SignedOCRResponse{}
	err := a.unmarshal(bytes.NewReader(*resp.Result), r)
	if err != nil {
		return nil, err
	}

	signers := []common.Address{}
	for _, n := range nodes {
		signers = append(signers, common.BytesToAddress(n.Signer[0:20]))
	}

	err = vaulttypes.ValidateSignatures(r, signers, int(don.F+1))
	if err != nil {
		return nil, fmt.Errorf("failed to validate signatures: %w", err)
	}
```
