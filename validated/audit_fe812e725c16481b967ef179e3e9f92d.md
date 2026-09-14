### Title
Per-workflow HTTP trigger rate limit can be bypassed by registering multiple workflow IDs under the same owner - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The gateway's `HTTPTriggerHandler.checkRateLimit` throttles incoming `workflows.execute` requests using a rate-limit bucket keyed by `workflowID`, not by the workflow owner/organization. Because a single owner can register many distinct workflows, the per-workflow cap can be multiplied simply by spreading requests across multiple workflow IDs, analogous to how `CAP_PER_ADDRESS` was bypassed in the reported audit finding by spreading mints across multiple subcontracts.

### Finding Description
`checkRateLimit` resolves the workflow reference for the given `workflowID` and calls `h.userRateLimiter.AllowErr(ctx)` with a context carrying `Workflow: workflowID` (and `Owner`/`Org` for settings resolution): [1](#0-0) 

The rate limiter is a settings-scoped limiter (`limits.RateLimiter` from `chainlink-common/pkg/settings/limits`) whose default scope, confirmed by the error-handling branch `case settings.ScopeWorkflow`, is per-workflow: a new bucket is created per distinct workflow key unless an owner/org-level override is explicitly configured: [2](#0-1) 

`workflowID` itself is either supplied directly by the caller or derived from `(workflowOwner, workflowName, workflowTag)` via `resolveWorkflowID`/`GetWorkflowID`, and any workflowID that has been registered in the DON's workflow metadata (`workflowMetadataHandler.GetWorkflowReference`) is accepted: [3](#0-2) 

Since the throttle key is the workflow identifier rather than the owner/org, an owner who registers N separate workflows (each requiring only a name/tag change, not a new blockchain identity or meaningfully higher cost) obtains N independent rate-limit buckets, and can route requests round-robin across them to achieve an aggregate throughput of `N × PerWorkflow.HTTPTrigger.RateLimit`. This mirrors the reported bug class: a nominal "per-entity" cap (`CAP_PER_ADDRESS` / here, per-workflow rate limit) is trivially multiplied by creating additional low-cost entities (subcontracts / additional workflow registrations) controlled by the same actor.

An org-level or owner-level override can mitigate this (as shown in `TestHttpTriggerHandler_CheckRateLimit_PerOrgOverride`), but that is opt-in configuration, not the default behavior — by default the scope is per-workflow.

### Impact Explanation
This allows a single unprivileged actor (workflow owner) to bypass the intended per-tenant throughput ceiling for the internet-facing HTTP trigger gateway, exceeding fair-use/DoS-protection limits and consuming disproportionate node/gateway/backend resources (outbound HTTP action budget, node send fan-out, response aggregation) relative to other tenants. It does not directly cause fund loss or authentication bypass, but it is a genuine quota-bypass affecting the shared gateway resource.

### Likelihood Explanation
Registering additional workflows is a normal, low-friction action already available to any workflow owner (no special privilege required beyond deploying/registering workflows they already control), making this readily exploitable by any user wanting more throughput than their configured per-workflow rate allows.

### Recommendation
Default the HTTP trigger rate limiter scope to the workflow owner (or org) rather than the individual workflow, or additionally enforce an owner/org-level aggregate cap alongside the per-workflow cap so that splitting traffic across multiple workflow IDs cannot multiply total allowed throughput.

### Proof of Concept
1. Owner `0xA` registers workflow `W1` (workflowID₁) and workflow `W2` (workflowID₂) — both cheap/normal registration operations.
2. Owner sends `workflows.execute` requests interleaved between `workflowID₁` and `workflowID₂`.
3. `checkRateLimit` (`http_trigger_handler.go:392`) creates/uses a separate `settings.ScopeWorkflow` bucket per workflowID, so each stream is allowed up to the full `PerWorkflow.HTTPTrigger.RateLimit`, giving the owner `2×` the intended throughput; repeating with N workflows yields `N×`.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L342-366)
```go
func (h *httpTriggerHandler) resolveWorkflowID(ctx context.Context, triggerReq *jsonrpc.Request[gateway_common.HTTPTriggerRequest], requestID string, callback handlers.Callback) (string, error) {
	h.lggr.Debugw("resolving workflow ID", "workflowID", triggerReq.Params.Workflow.WorkflowID, "workflowOwner", triggerReq.Params.Workflow.WorkflowOwner, "workflowName", triggerReq.Params.Workflow.WorkflowName, "workflowTag", triggerReq.Params.Workflow.WorkflowTag, "requestID", requestID)
	workflowID := triggerReq.Params.Workflow.WorkflowID
	if workflowID != "" {
		workflowID = normalizeHex(workflowID, workflowIDLength)
		_, found := h.workflowMetadataHandler.GetWorkflowReference(workflowID)
		if !found {
			h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, fmt.Sprintf("Workflow not found. 'workflowID' %s is not a valid workflow ID", workflowID), callback)
			return "", errors.New("workflow not found")
		}
		return workflowID, nil
	}
	workflowOwner := normalizeHex(triggerReq.Params.Workflow.WorkflowOwner, workflowOwnerLength)
	workflowName := "0x" + hex.EncodeToString([]byte(workflows.HashTruncateName(triggerReq.Params.Workflow.WorkflowName)))
	workflowID, found := h.workflowMetadataHandler.GetWorkflowID(
		workflowOwner,
		workflowName,
		triggerReq.Params.Workflow.WorkflowTag,
	)
	if !found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "Workflow not found. Provide either a valid 'workflowID' or a valid combination of 'workflowOwner', 'workflowName', and 'workflowTag'", callback)
		return "", errors.New("workflow not found")
	}
	return workflowID, nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L392-416)
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
```
