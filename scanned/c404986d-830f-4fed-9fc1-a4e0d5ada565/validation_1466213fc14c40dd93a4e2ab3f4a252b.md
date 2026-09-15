### Title
Unbounded per-request callback map in Gateway HTTP Trigger Handler with only rate-limit + time-based expiry, no hard cap on concurrently pending trigger requests - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The Besu advisory describes an unbounded server-side collection (`FilterRepository`'s `ConcurrentHashMap`) of client-created objects that live until explicitly polled/removed, with no cap enforced at creation time — only later fixed by adding a hard concurrency cap plus a time-based expiry. The `httpTriggerHandler` in Chainlink's Gateway exhibits the same structural pattern: it keeps a `map[string]savedCallback` (`h.callbacks`) that grows by one entry per unique `req.ID` on every `workflows.execute` trigger request, and removal only happens via a periodic reaper based on age (`CleanUpPeriodMs`), not via any explicit cap on the number of concurrently-tracked callbacks.

### Finding Description
`httpTriggerHandler.callbacks` is a plain Go map guarded by `callbacksMu`, initialized empty and populated by `setupCallback` for every incoming trigger request that passes validation/authorization/rate-limiting [1](#0-0) . Each successfully validated request adds an entry keyed by the caller-supplied `req.ID` and is only removed by `reapExpiredCallbacks`, which walks the entire map and deletes entries older than `CleanUpPeriodMs` [2](#0-1) . There is no check of `len(h.callbacks)` against a maximum before insertion anywhere in `HandleUserTriggerRequest` or `setupCallback` — the only gating mechanisms observed before an entry is added are per-request validation (`validatedTriggerRequest`), workflow-ID resolution, request authorization, and a rate limiter (`checkRateLimit`, backed by `userRateLimiter` with configurable global/per-sender RPS and burst) [3](#0-2) . Rate limiting throttles the *rate* of insertion but does not bound the *total number* of entries that can accumulate before the next reap cycle, which is the exact gap the Besu advisory targeted (no per-connection/per-user/global cap on concurrently active items, relying solely on time-based expiry).

### Impact Explanation
Because the cleanup interval defaults to 600000ms (10 minutes) per the handler's documented config [4](#0-3) , an authorized/rate-limited caller sustaining traffic near the configured RPS/burst limits for the full cleanup window can accumulate a correspondingly large number of live `savedCallback` entries (each holding response-aggregator state per shard) before any of them are reaped, growing gateway node memory. This is analogous to, but less severe than, the Besu case since a rate limiter is present; the missing control is specifically the absence of a hard concurrency cap independent of the time-based rate limiter, which was exactly the additional mitigation Besu's fix (`--rpc-max-active-filters`) added on top of expiry.

### Likelihood Explanation
Reaching this path only requires being an authorized caller of the Gateway's HTTP trigger endpoint (JWT-based per-workflow auth, per the handler's documented security model) able to send trigger requests at or near the configured rate limits over a sustained period — no privileged/operator access or node compromise is required. However, unlike the Besu case (which had literally no cap and no rate limiter, so a single unauthenticated client could grow memory arbitrarily fast), this Chainlink path is throttled by `userRateLimiter`, so the practical growth rate and blast radius are meaningfully smaller and bounded by the configured rate limiter and cleanup interval.

### Recommendation
Add an explicit cap on `len(h.callbacks)` enforced at insertion time in `setupCallback`/`HandleUserTriggerRequest` (rejecting new requests once a configurable maximum concurrent-callbacks threshold is reached, similar to Besu's `FilterCountExceededException`), independent of the existing rate limiter, and consider shortening/making configurable the reap interval relative to the rate limit ceiling so worst-case memory is bounded by a known constant rather than by `rate_limit * cleanup_interval`.

### Proof of Concept
Not independently verifiable from static code alone — would require exercising an authorized session against a running Gateway node, sending sustained `workflows.execute` trigger requests at the configured per-sender RPS/burst for a duration approaching `CleanUpPeriodMs`, and observing `h.callbacks` map growth via `RecordPendingRequestsCount` metrics [5](#0-4)  before the next reap cycle fires.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L58-93)
```go
type httpTriggerHandler struct {
	services.StateMachine
	config                  ServiceConfig
	shards                  []*shardEndpoint
	nodeAddrToShard         map[string]*shardEndpoint
	lggr                    logger.Logger
	callbacksMu             sync.Mutex
	callbacks               map[string]savedCallback // requestID -> savedCallback
	stopCh                  services.StopChan
	workflowMetadataHandler *WorkflowMetadataHandler
	userRateLimiter         limits.RateLimiter
	metrics                 *metrics.Metrics
	wg                      sync.WaitGroup
	orgResolver             orgresolver.OrgResolver // optional; nil if the node isn't configured to resolve orgs (e.g. no Linking Service)
}

type HTTPTriggerHandler interface {
	job.ServiceCtx
	HandleUserTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback, requestStartTime time.Time) error
	HandleNodeTriggerResponse(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error
}

func NewHTTPTriggerHandler(lggr logger.Logger, cfg ServiceConfig, shards []*shardEndpoint, nodeAddrToShard map[string]*shardEndpoint, workflowMetadataHandler *WorkflowMetadataHandler, userRateLimiter limits.RateLimiter, metrics *metrics.Metrics, orgResolver orgresolver.OrgResolver) *httpTriggerHandler {
	return &httpTriggerHandler{
		lggr:                    logger.Named(lggr, "RequestCallbacks"),
		callbacks:               make(map[string]savedCallback),
		config:                  cfg,
		shards:                  shards,
		nodeAddrToShard:         nodeAddrToShard,
		stopCh:                  make(services.StopChan),
		workflowMetadataHandler: workflowMetadataHandler,
		userRateLimiter:         userRateLimiter,
		metrics:                 metrics,
		orgResolver:             orgResolver,
	}
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-146)
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

	strippedWorkflowID := strings.TrimPrefix(workflowID, "0x")
	legacyExecutionID, err := workflows.EncodeExecutionID(strippedWorkflowID, req.ID) //nolint:staticcheck // legacy ID kept for observability comparison
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error generating execution ID: " + err.Error())
	}
	// Workflows shouldn't use more than one HTTP trigger. If we ever need to support multiple triggers, we'd need to pass
	// trigger index to the Gateway handler and somehow allow senders to pick. For now, we use trigger index 0.
	// Execution IDs here are used only for logging.
	executionIDWithTriggerIndex, err := workflows.GenerateExecutionIDWithTriggerIndex(strippedWorkflowID, req.ID, 0)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error generating execution ID with trigger index: " + err.Error())
	}
	h.lggr.Debugw("processing request",
		"legacyExecutionID", legacyExecutionID,
		"executionIDWithTriggerIndex", executionIDWithTriggerIndex,
		"requestID", req.ID,
		"workflowID", workflowID)

	reqWithKey, err := reqWithAuthorizedKey(triggerReq, *key)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error marshaling trigger request: " + err.Error())
	}

	doneCh, err := h.setupCallback(ctx, req.ID, callback, requestStartTime, workflowID)
	if err != nil {
		return err
	}

	return h.sendWithRetries(ctx, legacyExecutionID, executionIDWithTriggerIndex, reqWithKey, workflowID, doneCh)
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L561-581)
```go
// reapExpiredCallbacks removes callbacks that are older than the maximum age
func (h *httpTriggerHandler) reapExpiredCallbacks(ctx context.Context) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()
	now := time.Now()
	var expiredCount int
	for reqID, callback := range h.callbacks {
		if now.Sub(callback.createdAt) > time.Duration(h.config.CleanUpPeriodMs)*time.Millisecond {
			if !callback.processed {
				h.metrics.IncrementRequestErrors(ctx, jsonrpc.ErrInternal, h.lggr)
			}
			h.cleanupCallback(reqID)
			expiredCount++
		}
	}
	if expiredCount > 0 {
		h.metrics.IncrementPendingRequestsCleanUpCount(ctx, int64(expiredCount), h.lggr)
		h.lggr.Infow("Removed expired callbacks", "count", expiredCount, "remaining", len(h.callbacks))
	}
	h.metrics.RecordPendingRequestsCount(ctx, int64(len(h.callbacks)), h.lggr)
}
```

**File:** core/services/gateway/handlers/capabilities/v2/README.md (L194-197)
```markdown
  "cleanUpPeriodMs": 600000,
  "metadataPullIntervalMs": 60000,
  "metadataAggregationIntervalMs": 60000,
  "outboundRequestCacheTTLMs": 600000
```
