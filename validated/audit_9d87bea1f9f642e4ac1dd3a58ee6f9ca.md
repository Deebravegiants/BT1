### Title
Webhook Authorizer Uses Stale Cached Decision Instead of Live Authorization State, Allowing Actions After Permission Revocation - (File: `staging/src/k8s.io/apiserver/plugin/pkg/authorizer/webhook/webhook.go`)

### Summary
The Kubernetes webhook authorizer caches "allowed" `SubjectAccessReview` decisions in an internal `responseCache` for a configurable `AuthorizedTTL` (default 5 minutes) instead of consulting the authoritative source (the remote authorization webhook / underlying RBAC state) on every request. This mirrors the reported bug class: a security/administrative decision (`redelegate_lp`'s use of `pool.amount`) is made from an internal tracker value that can silently diverge from the true, current state (actual staked amount), rather than querying the authoritative source live.

### Finding Description
`WebhookAuthorizer.Authorize` computes a cache key from the request's `SubjectAccessReviewSpec` and, on a cache hit, reuses the previously stored `SubjectAccessReviewStatus` without re-verifying against the current authorization state: [1](#0-0) 
If the decision was `Allowed`, it is cached using `authorizedTTL`: [2](#0-1) 
The `WebhookAuthorizer` struct stores this cache and its TTLs directly, with defaults of 5 minutes for authorized responses: [3](#0-2) [4](#0-3) 

Just as `redelegate_lp` trusted `pool.amount` (an internal tracker that could be stale relative to the real staked amount due to unaccounted rewards/slashing) instead of querying the live `mstaking` state, the webhook authorizer trusts a cached `Allow` decision (an internal tracker of a prior authorization state) instead of re-querying the authoritative policy source, for up to the configured TTL.

### Impact Explanation
If a cluster administrator revokes a user's/service account's permissions (e.g., removes a RoleBinding backing a webhook policy, or the webhook backend's policy changes to deny), any previously cached `Allow` decision for that exact request signature remains valid and is reused by the API server for up to `AuthorizedTTL` (default 5 minutes) after the change takes effect. This creates a window in which an unprivileged/de-privileged user can continue performing actions they should no longer be authorized for — a direct authorization-bypass analog to the reported bug's "orphaned/incorrect state due to stale internal tracker" impact.

### Likelihood Explanation
This is a designed, always-active caching behavior (not an edge case), enabled by default whenever a webhook authorizer is configured (`CacheAuthorizedRequests` defaults to true). Any revocation of previously-granted access is subject to this stale-cache window until the TTL expires, making the exposure window deterministic and easily triggered whenever permissions change during active use — analogous to the "High" likelihood rated in the original report for tracker drift.

### Recommendation
Reduce reliance on time-based caching for authorization decisions that grant access, or invalidate cache entries proactively when underlying RBAC/webhook policy changes are observed (e.g., via watch-triggered cache invalidation) rather than relying purely on TTL expiry, mirroring the report's recommendation to query the authoritative live state instead of an internal tracker.

### Proof of Concept
1. Configure the API server with a webhook authorizer and default `AuthorizedTTL` (5m).
2. As an admin, grant a user permission to perform `get pods` in namespace `ns1`; the user issues the request, and the webhook returns `Allowed`, which is cached by `w.responseCache.Add(...)`.
3. The admin immediately revokes the permission (deletes the RoleBinding / updates the webhook backend policy).
4. Within the next ~5 minutes, the same user re-issues the identical `get pods` request; because the cache key (derived solely from the `SubjectAccessReviewSpec`) still matches, `Authorize` returns the previously cached `Allow` decision without contacting the webhook, permitting access that should have been denied.

### Citations

**File:** staging/src/k8s.io/apiserver/plugin/pkg/authorizer/webhook/webhook.go (L70-79)
```go
type WebhookAuthorizer struct {
	subjectAccessReview subjectAccessReviewer
	responseCache       *cache.LRUExpireCache
	authorizedTTL       time.Duration
	unauthorizedTTL     time.Duration
	retryBackoff        wait.Backoff
	decisionOnError     authorizer.Decision
	metrics             metrics.AuthorizerMetrics
	celMatcher          *authorizationcel.CELMatcher
	name                string
```

**File:** staging/src/k8s.io/apiserver/plugin/pkg/authorizer/webhook/webhook.go (L220-226)
```go
	key, err := json.Marshal(r.Spec)
	if err != nil {
		return w.decisionOnError, "", err
	}
	if entry, ok := w.responseCache.Get(string(key)); ok {
		r.Status = entry.(authorizationv1.SubjectAccessReviewStatus)
	} else {
```

**File:** staging/src/k8s.io/apiserver/plugin/pkg/authorizer/webhook/webhook.go (L274-281)
```go
		r.Status = result.Status
		if shouldCache(attr) {
			if r.Status.Allowed {
				w.responseCache.Add(string(key), r.Status, w.authorizedTTL)
			} else {
				w.responseCache.Add(string(key), r.Status, w.unauthorizedTTL)
			}
		}
```

**File:** staging/src/k8s.io/apiserver/pkg/apis/apiserver/v1/types.go (L461-472)
```go
type WebhookConfiguration struct {
	// The duration to cache 'authorized' responses from the webhook
	// authorizer.
	// Same as setting `--authorization-webhook-cache-authorized-ttl` flag
	// Default: 5m0s
	AuthorizedTTL metav1.Duration `json:"authorizedTTL"`
	// CacheAuthorizedRequests specifies whether authorized requests should be cached.
	// If set to true, the TTL for cached decisions can be configured via the
	// AuthorizedTTL field.
	// Default: true
	// +optional
	CacheAuthorizedRequests *bool `json:"cacheAuthorizedRequests,omitempty"`
```
