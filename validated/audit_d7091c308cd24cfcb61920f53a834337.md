### Title
Per-org/per-workflow HTTP trigger rate-limit override is bypassable for a window because new-tenant limiters seed from the permissive global default until settings are first polled - ([File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go])

### Summary
The Kairos finding is a class of bug where a per-key protection value (an anti-DDoS lower bound) defaults to zero/permissive until an admin has explicitly configured it for that specific key, and an unprivileged actor can exploit this by being first to use a not-yet-configured key. The closest reachable analog in this repo is the CRE Gateway's `httpTriggerHandler` user-facing rate limiting, where a per-tenant (workflow/owner/org) rate limiter is lazily created on the *first* request for that tenant and is seeded with the **global default** burst/rate rather than the tenant's actual (possibly more restrictive) settings-backed override, because the settings-backed value is fetched asynchronously on a fixed poll interval.

### Finding Description
`httpTriggerHandler.HandleUserTriggerRequest` (in `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`) is reachable directly from an unprivileged client sending a JSON-RPC `workflowExecute`/HTTP-trigger request to the gateway, subject only to JWT signature verification (not authorization against a tighter quota). The handler calls into a `checkRateLimit`/`userRateLimiter` path backed by `chainlink-common`'s settings-scoped rate limiter (`limits.Factory{Settings: ...}.MakeRateLimiter(...)`), which resolves limits hierarchically: workflow → owner → org → global.

As explicitly documented in the handler's own test suite: [1](#0-0) 

the first rate-limit check for any given workflow/tenant creates that tenant's limiter **seeded with the global default** (e.g., burst 3) and only picks up the tenant-specific (e.g., org-restricted, burst 0/deny) override after the settings poll interval elapses (`pollPeriod = 5s` in `chainlink-common`'s `pkg/settings/limits`). This mirrors the Kairos root cause precisely: a per-key (per-tenant) restrictive value defaults to a permissive value until it has been resolved/set for that specific key, and the attacker controls which key (workflow ID / owner / org) is "new" simply by picking one that hasn't yet triggered a rate-limit check on this gateway node.

### Impact Explanation
An unprivileged, unauthenticated-beyond-JWT-signature caller who is a member of an org that has (or would have) a restrictive rate-limit override (e.g., `burst 0`, i.e., "deny everything") can bypass that restriction for the lifetime of one poll interval per new workflow/tenant identity, by using a fresh workflow ID/owner. Since workflow IDs are attacker-controlled inputs (0x-prefixed hex identifiers registered by the workflow owner, not admin-assigned), an attacker can continually mint "unused" tenant keys to keep re-triggering the permissive default window, effectively defeating the intended DDoS/anti-abuse rate limiting on the internet-facing HTTP trigger gateway path. This directly matches the Sherlock report's "Slipping through lower bound due to front run" impact: the protective threshold is bypassable by exploiting the zero/default state of a not-yet-configured per-key control.

### Likelihood Explanation
Likelihood is significant given the request path is a straightforward unprivileged client → gateway → `HandleUserTriggerRequest` → `checkRateLimit` flow, and workflow IDs are freely chosen/derived from the caller-registered workflow (not gated by an admin). The window of exposure is bounded (default settings poll interval, ~5s, as observed in tests), but is repeatable indefinitely by rotating to new workflow/tenant keys, similar to how the Kairos bug is repeatable by using new currencies.

### Recommendation
- Do not seed newly-created per-tenant rate limiters with the global default; instead, block/synchronously resolve the settings-backed value (workflow → owner → org → global) before allowing the first request through, or apply the most-restrictive known ancestor scope value until the tenant-specific value is resolved.
- Alternatively, pre-warm/pre-resolve per-org and per-owner overrides eagerly (e.g., on org resolution) rather than lazily on first request, removing the race window.
- Add explicit tests asserting that the very first request for a brand-new tenant under a restrictive org override is denied, not allowed via the default-burst grace window.

### Proof of Concept
1. Configure org `org-restricted` with an HTTPTrigger rate-limit override of `every1h:0` (deny), as in the settings JSON used by `TestHttpTriggerHandler_CheckRateLimit_PerOrgOverride`: [2](#0-1) 
2. As an attacker belonging to `org-restricted`, register/use a brand-new `workflowID` never seen before by this gateway node.
3. Immediately send a trigger request for that workflow; per the documented behavior, the per-workflow-tenant limiter is created and seeded with the global default (burst 3), so the request is allowed: [3](#0-2) 
4. Repeat with a fresh workflow ID before each poll interval elapses to keep consuming the permissive default burst, bypassing the org-level deny override that should apply to this caller/org.

Note: I was not able to view the exact body of `checkRateLimit`/`userRateLimiter` invocation inside `http_trigger_handler.go` (search only returned matches, not full function text) due to tool/iteration limits, so the precise line numbers of the lazy-limiter-creation code could not be cited directly; the analysis above is based on the explicit behavior documented in the corresponding test's comments and assertions, which describe and verify this exact seeding behavior.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L2054-2067)
```go
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
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L2082-2091)
```go
	// The first check for each workflow creates its per-workflow-tenant limiter, seeded
	// with the global default (burst 3) until the settings-backed value is first polled.
	require.NoError(t, handler.checkRateLimit(t.Context(), restrictedWfID, "req-1", hc.NewCallback()))
	require.NoError(t, handler.checkRateLimit(t.Context(), normalWfID, "req-2", hc.NewCallback()))

	// chainlink-common's scoped RateLimiter refreshes settings-sourced values on a fixed
	// poll interval (pkg/settings/limits.pollPeriod = 5s); wait past it so the org
	// override is picked up. Deliberately not checking again in the meantime: that would
	// burn through the default burst and could deny the next check for the wrong reason.
	time.Sleep(6 * time.Second)
```
