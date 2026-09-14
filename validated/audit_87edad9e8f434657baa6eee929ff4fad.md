### Title
Per-workflow rate limits are seeded from the permissive global default and only apply org/owner-scoped quota overrides after an asynchronous polling delay, allowing quota bypass - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The HTTP Trigger Handler's `checkRateLimit` resolves an org/owner scope via `orgResolver` and enforces a rate limit through a settings-backed `limits.RateLimiter`. The underlying scoped rate limiter is lazily created per workflow on first use and is seeded with the global default limit; any org- or owner-specific override configured in settings is only picked up after a fixed background poll interval elapses. This mirrors the Munchables `LandManager` finding: a per-entity quota/permission value (tax rate / rate limit) is not applied atomically at first use, so unprivileged requesters can operate under a stale, more permissive default value for a window of time before the authoritative (more restrictive) configuration takes effect.

### Finding Description
`httpTriggerHandler.checkRateLimit` resolves the caller's org and applies the rate limiter: [1](#0-0) 

The per-workflow scoped limiter honors a settings hierarchy (workflow → owner → org → global), but as demonstrated by the test itself, the first check for a given workflow creates its tenant-scoped limiter instance seeded with the *global default* burst, and the org-specific override is only applied after the settings poller's fixed interval (5 seconds) elapses: [2](#0-1) 

This is functionally identical to the Munchables bug class: a per-entity configuration value (tax rate in the report; rate-limit quota here) that should immediately reflect the authoritative/restrictive setting is instead read from a default/cached value until an out-of-band synchronization step completes. In Munchables, `plotMetadata[landlord].currentTaxRate` defaulted to 0% until `triggerPlotMetadata`/`updatePlotMetadata` ran; here, the scoped rate limiter defaults to the permissive global limit until the settings poll (`pollPeriod`) refreshes the org override.

### Impact Explanation
An unprivileged workflow owner belonging to an org that has been assigned a restrictive (or zero) HTTP Trigger rate limit via org-scoped settings can still issue requests up to the global default burst/rate for any newly-instantiated per-workflow limiter, before the org override is polled in. Because the limiter is created per workflow ID (lazily, on first check), an actor could repeat this by registering new workflow IDs, each starting a fresh "grace window" seeded with the permissive global default before the restrictive org-level override converges. This is a quota-bypass condition on the internet-facing gateway trigger path, consistent with the finding class explicitly accepted by the rules ("allowlist or quota bypass").

The impact is bounded: it is a transient (bounded by the poll interval, default ~5s per the test comment) elevation of allowed request rate rather than a full authentication bypass, similar to how the original finding's impact was judged Medium/borderline because the exposure window is bounded rather than unlimited.

### Likelihood Explanation
The vulnerable path (`HandleUserTriggerRequest` → `checkRateLimit` → `resolveOrgID` → settings-backed `RateLimiter`) is reachable directly from an unauthenticated/unprivileged external HTTP trigger request to the gateway — no special node or operator privilege is required to trigger it, only a registered workflow whose owner belongs to a rate-limited org. Any newly registered or first-invoked workflow is subject to this default-seeding window, so likelihood of the race being exploitable is fairly high whenever an org boundary is used to apply differentiated/restrictive throttling (e.g., for abusive tenants or paid-tier gating).

### Recommendation
- Ensure per-workflow/owner/org scoped rate limiters synchronously resolve (or block on) the authoritative settings value on first creation rather than defaulting to the global permissive value while polling completes.
- Alternatively, seed newly created scoped limiters with the most restrictive known value (fail-closed) until the authoritative override is confirmed, rather than fail-open to the global default.
- Reduce or eliminate the window between workflow/owner/org resolution and rate-limit enforcement, and consider re-checking/re-applying the override immediately upon limiter creation instead of waiting for the next poll tick.

### Proof of Concept
Based on `TestHttpTriggerHandler_CheckRateLimit_PerOrgOverride`: [3](#0-2) 

1. Org `org-restricted` is configured via settings with `PerWorkflow.HTTPTrigger.RateLimit = "every1h:0"` (i.e., deny all).
2. A workflow owned by an address in `org-restricted` issues its first HTTP trigger request. Because the workflow's per-tenant limiter is created on first check and seeded from the global default (burst 3), `checkRateLimit` succeeds (`handler.checkRateLimit(...)` returns `nil`) even though the org's configured limit is 0.
3. Only after the settings poll interval elapses (test sleeps 6s past the 5s `pollPeriod`) does a subsequent request correctly get denied with `jsonrpc.ErrLimitExceeded`.
4. Repeating step 2 with newly registered workflow IDs for the same restricted org re-creates a fresh limiter each time, re-obtaining the permissive global-default grace window and bypassing the org's configured quota repeatedly.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L378-416)
```go
// resolveOrgID resolves the organization ID for owner, or returns "" if it can't be resolved
func (h *httpTriggerHandler) resolveOrgID(ctx context.Context, owner string) string {
	if h.orgResolver == nil {
		h.lggr.Warnw("OrgResolver is nil, continuing without an orgID", "workflowOwner", owner)
		return ""
	}
	orgID, err := h.orgResolver.Get(ctx, owner)
	if err != nil {
		h.lggr.Warnw("Failed to resolve organization ID, continuing without it", "workflowOwner", owner, "err", err)
		return ""
	}
	return orgID
}

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L2040-2103)
```go
func TestHttpTriggerHandler_CheckRateLimit_PerOrgOverride(t *testing.T) {
	t.Parallel()

	const (
		restrictedOrg   = "org-restricted"
		restrictedOwner = "0x1111111111111111111111111111111111aaaa"
		restrictedWfID  = "0x1111"
		normalOrg       = "org-normal"
		normalOwner     = "0x2222222222222222222222222222222222bbbb"
		normalWfID      = "0x2222"
	)

	// Only org-restricted gets an override (burst 0: deny everything); org-normal (and
	// everything else) falls through to the global default (every 30s, burst 3).
	getter, err := settings.NewJSONGetter([]byte(`{
		"org": {
			"org-restricted": {
				"PerWorkflow": {
					"HTTPTrigger": {
						"RateLimit": "every1h:0"
					}
				}
			}
		}
	}`))
	require.NoError(t, err)

	rateLimiter, err := limits.Factory{Settings: getter}.MakeRateLimiter(cresettings.Default.PerWorkflow.HTTPTrigger.RateLimit)
	require.NoError(t, err)

	orgResolver := &stubOrgResolver{orgByOwner: map[string]string{
		restrictedOwner: restrictedOrg,
		normalOwner:     normalOrg,
	}}

	metadataHandler := createTestMetadataHandler(t)
	metadataHandler.workflowIDToRef[restrictedWfID] = workflowReference{workflowOwner: restrictedOwner, workflowName: "wf-restricted", workflowTag: "v1"}
	metadataHandler.workflowIDToRef[normalWfID] = workflowReference{workflowOwner: normalOwner, workflowName: "wf-normal", workflowTag: "v1"}

	testMetrics := createTestMetrics(t, &config.DONConfig{Members: []config.NodeConfig{{Address: "node1"}}})
	handler := NewHTTPTriggerHandler(logger.Test(t), WithDefaults(ServiceConfig{}), nil, nil, metadataHandler, rateLimiter, testMetrics, orgResolver)

	// The first check for each workflow creates its per-workflow-tenant limiter, seeded
	// with the global default (burst 3) until the settings-backed value is first polled.
	require.NoError(t, handler.checkRateLimit(t.Context(), restrictedWfID, "req-1", hc.NewCallback()))
	require.NoError(t, handler.checkRateLimit(t.Context(), normalWfID, "req-2", hc.NewCallback()))

	// chainlink-common's scoped RateLimiter refreshes settings-sourced values on a fixed
	// poll interval (pkg/settings/limits.pollPeriod = 5s); wait past it so the org
	// override is picked up. Deliberately not checking again in the meantime: that would
	// burn through the default burst and could deny the next check for the wrong reason.
	time.Sleep(6 * time.Second)

	// org-restricted's override (burst 0) is now active: denied.
	callback := hc.NewCallback()
	err = handler.checkRateLimit(t.Context(), restrictedWfID, "req-3", callback)
	require.Error(t, err)
	payload, waitErr := callback.Wait(t.Context())
	require.NoError(t, waitErr)
	requireUserErrorSent(t, payload, jsonrpc.ErrLimitExceeded)

	// org-normal has no override and still has burst left over from the global default: allowed.
	require.NoError(t, handler.checkRateLimit(t.Context(), normalWfID, "req-4", hc.NewCallback()))
}
```
