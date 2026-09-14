### Title
Rate limit checked only after expensive JWT authorization in HTTP trigger handler, enabling fee-free computational flood - (File: `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`)

### Summary
`httpTriggerHandler.HandleUserTriggerRequest` performs full JWT-based authorization (`authorizeRequest`) before ever consulting the per-workflow rate limiter (`checkRateLimit`). Because the workflow rate limit is enforced only after the costly signature-verification step, an unprivileged remote caller can send unlimited forged/invalid `HTTPTriggerRequest` messages against any known (public) `workflowID` and force the gateway to perform cryptographic JWT verification work on every one of them, at no cost and with no throttling until after that work is already done — the same "rate limit enforced only in the dispatch body, after the expensive/free-to-attacker step" pattern described in the Bittensor `set_weights`/`commit_weights` GHSA-2026-006 analog.

### Finding Description
`HandleUserTriggerRequest` executes its checks in this order: [1](#0-0) 

1. `validatedTriggerRequest` — cheap JSON parsing/field validation.
2. `resolveWorkflowID` — a map lookup keyed by a public workflow identifier (workflow IDs/owners/names are not secrets; they originate from the on-chain `WorkflowRegistry`) [2](#0-1) .
3. `authorizeRequest` — calls `h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)`, which performs JWT signature verification, an expensive cryptographic operation [3](#0-2) .
4. Only **after** authorization succeeds does the code call `checkRateLimit`, which resolves the org/owner and applies a per-workflow rate limiter [4](#0-3) .

If `authorizeRequest` fails (e.g., an attacker submits an invalid/forged signature for a known workflow ID), the function returns immediately at step 3 and `checkRateLimit` is never invoked [5](#0-4) . This mirrors the reported bug class: the "rate limit" that is supposed to bound the cost of processing is enforced only deep inside the dispatch path, after the expensive verification work has already run, so failed/forged requests are effectively free to send and unbounded in volume.

### Impact Explanation
This is an internet-facing Gateway HTTP-trigger endpoint (per the V2 README, "HTTP Triggers: Inbound requests that trigger workflow executions with JWT-based authentication") [6](#0-5) . Any unprivileged remote actor who knows (or brute-forces/enumerates, since workflow selectors are public on-chain data) a `workflowID` can flood the gateway with forged-signature requests. Each request forces a full JWT signature verification before hitting any throttle, allowing CPU-exhaustion / denial-of-service against the gateway node with no cost or credential required by the attacker — analogous to fee-free flooding via `Pays::No` dispatch calls whose rate limit is only checked inside the dispatch body.

### Likelihood Explanation
Likelihood is moderate: the attacker needs a valid `workflowID` (public/discoverable), but no valid signing key or session — they can submit arbitrary/garbage `Auth` JWTs and still force the server through the expensive verification path before any limiter fires. I could not fully verify from the available index whether an outer network-layer limiter (e.g., per-IP/global limiter in `core/services/gateway/gateway.go` or the transport layer ahead of `HandleUserTriggerRequest`) mitigates this before the request reaches `authorizeRequest`; this should be confirmed, as it affects the actual exploitability of the flood.

### Recommendation
Move a cheap, pre-authorization rate/quota check (e.g., per-IP or per-workflow-ID token bucket keyed off data available before signature verification) ahead of `authorizeRequest`, so failed-authorization attempts are throttled before the costly JWT verification is performed, not only after a successful authorization.

### Proof of Concept
1. Identify a valid, public `workflowID` (from on-chain `WorkflowRegistry` or workflow metadata sync).
2. Send repeated `workflows.execute` JSON-RPC requests to the gateway's HTTP trigger endpoint with that `workflowID` and an arbitrary/invalid `Auth` JWT.
3. Observe that each request reaches `authorizeRequest` → `workflowMetadataHandler.Authorize` (full signature verification) and fails there, before `checkRateLimit` is ever called — i.e., there is no bound on the number of such verification attempts, as shown by the code path in `HandleUserTriggerRequest` [1](#0-0) .

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L34-41)
```go
const (
	// Reference: https://github.com/smartcontractkit/chainlink-evm/blob/develop/contracts/src/v0.8/workflow/dev/v2/WorkflowRegistry.sol
	workflowIDLength       = 66 // 0x + 64 hex characters = 32 bytes
	workflowOwnerLength    = 42 // 0x + 40 hex characters = 20 bytes
	maxWorkflowNameLength  = 64 // Maximum workflow name length
	WorkflowNameHashLength = 22 // 0x + 20 hex characters = 10 bytes
	maxWorkflowTagLength   = 32 // Maximum workflow tag length
)
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-113)
```go
func (h *httpTriggerHandler) HandleUserTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback, requestStartTime time.Time) error {
	triggerReq, err := h.validatedTriggerRequest(ctx, req, callback)
	if err != nil {
		return err
	}

	workflowID, err := h.resolveWorkflowID(ctx, triggerReq, req.ID, callback)
	if err != nil {
		return err
	}

	key, err := h.authorizeRequest(ctx, workflowID, req, callback)
	if err != nil {
		return err
	}

	if err = h.checkRateLimit(ctx, workflowID, req.ID, callback); err != nil {
		return err
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L368-376)
```go
func (h *httpTriggerHandler) authorizeRequest(ctx context.Context, workflowID string, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback) (*gateway_common.AuthorizedKey, error) {
	h.lggr.Debugw("authorizing request", "workflowID", workflowID, "requestID", req.ID)
	key, err := h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInvalidRequest, "Auth failure: "+err.Error(), callback)
		return nil, errors.Join(errors.New("auth failure"), err)
	}
	return key, nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L392-417)
```go
func (h *httpTriggerHandler) checkRateLimit(ctx context.Context, workflowID, requestID string, callback handlers.Callback) error {
	workflowRef, found := h.workflowMetadataHandler.GetWorkflowReference(workflowID)
	if !found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "workflow reference not found", callback)
		return errors.New("workflow reference not found")
	}

	orgID := h.resolveOrgID(ctx, workflowRef.workflowOwner)
	ctx = contexts.WithCRE(ctx, contexts.CRE{Owner: workflowRef.workflowOwner, Org: orgID, Workflow: workflowID})
	if err := h.userRateLimiter.AllowErr(ctx); err != nil {
		lggr := logger.With(h.lggr, platform.KeyWorkflowID, workflowID, platform.KeyWorkflowOwner, workflowRef.workflowOwner, "requestID", requestID, "err", err)
		if errLimited, ok := errors.AsType[limits.ErrorRateLimited](err); ok {
			switch errLimited.Scope {
			case settings.ScopeWorkflow:
				lggr.Errorf("failed to start execution: per workflow rate limit exceeded")
				h.metrics.IncrementWorkflowThrottled(ctx, h.lggr)
			default:
				lggr.Errorf("failed to start execution: unexpected rate limit for scope %s", errLimited.Scope)
			}
			h.handleUserError(ctx, requestID, jsonrpc.ErrLimitExceeded, "rate limit exceeded", callback)
			return err
		}
		return fmt.Errorf("failed to check rate limit: %w", err)
	}
	return nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L17-19)
```markdown

- **HTTP Actions**: Outbound HTTP requests with caching, rate limiting
- **HTTP Triggers**: Inbound requests that trigger workflow executions with JWT-based authentication
```
