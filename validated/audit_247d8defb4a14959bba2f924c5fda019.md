### Title
ResourceQuota admission bypasses `LimitedResources` scope-gating for pods that only partially satisfy a multi-expression `ScopeSelector` - ([File: staging/src/k8s.io/apiserver/pkg/admission/plugin/resourcequota/controller.go])

### Summary
`CheckRequest` builds `restrictedScopes` by calling `evaluator.MatchingScopes` on each quota's *individual* scope-selector expressions, rather than requiring that the pod satisfy the whole `ScopeSelector` conjunction the way `evaluator.Matches` does. `UncoveredQuotaScopes` then only compares `ScopeName` values between `limitedScopes` and `restrictedScopes`, so a pod that matches just one expression of a multi-expression quota selector is treated as "covered" even though that same quota's `Matches()` call (which requires ALL expressions to match) rejects it and never enforces any hard limit on it.

### Finding Description
In `CheckRequest` (`staging/src/k8s.io/apiserver/pkg/admission/plugin/resourcequota/controller.go`):

- `limitedScopes` is computed via `getMatchedLimitedScopes`, which calls `evaluator.MatchingScopes(inputObject, limitedResource.MatchScopes)` for each admission-config `LimitedResource` [1](#0-0) .
- For every namespace `ResourceQuota`, the code separately computes `localRestrictedScopes, err := evaluator.MatchingScopes(inputObject, scopeSelectors)` and appends it into `restrictedScopes`, using the quota's full selector list [2](#0-1) .
- Crucially, `evaluator.MatchingScopes` for pods (`pkg/quota/v1/evaluator/core/pods.go`) evaluates each `ScopedResourceSelectorRequirement` **independently** and returns any that individually match, with no AND semantics across the quota's whole scope selector [3](#0-2) .
- By contrast, whether a quota actually applies to (and enforces hard limits on) the pod is decided separately by `evaluator.Matches(&resourceQuota, inputObject)`, which correctly ANDs all scope selectors of that quota via `generic.Matches` (`matchScope = matchScope && innerMatch`) [4](#0-3) . If that AND fails, the quota is skipped and never added to `interestingQuotaIndexes`/`restrictedResourcesSet` [5](#0-4) .
- Finally, `UncoveredQuotaScopes` (`pkg/quota/v1/evaluator/core/pods.go`) only compares `ScopeName`, ignoring `Operator`/`Values`, and ignores which quota an entry came from: `if matchedScopeSelector.ScopeName == selector.ScopeName { isCovered = true }` [6](#0-5)  and the result feeds directly into the admission decision at `staging/src/k8s.io/apiserver/pkg/admission/plugin/resourcequota/controller.go:586-592` [7](#0-6) .

**Exploit flow:** a cluster admin configures the ResourceQuota admission plugin's `Configuration.LimitedResources` to require a covering quota for a scope (e.g. `PriorityClass=high`), and a namespace `ResourceQuota` exists whose `ScopeSelector.MatchExpressions` combines *two* conditions with AND semantics, e.g. `{PriorityClass In [high]}` AND `{BestEffort Exists}`. An attacker with only `create` rights on Pods (and `get` on the ResourceQuota to learn its selector) submits a pod with `priorityClassName: high` but with explicit resource requests/limits set (i.e. not BestEffort). `limitedScopes` matches `PriorityClass=high`. For the quota, `MatchingScopes` independently matches the `PriorityClass` sub-expression (even though `BestEffort` sub-expression fails), so `restrictedScopes` also contains `PriorityClass=high`. `evaluator.Matches` correctly determines the quota does NOT apply (AND fails), so no hard-limit accounting happens for this pod against that quota. But `UncoveredQuotaScopes` sees `PriorityClass` present in both lists and reports full coverage, so the "must be covered by quota" check silently passes — the pod is admitted without any quota ever actually constraining it, even though the admin's `LimitedResources` policy was meant to gate exactly this scope.

### Impact Explanation
This defeats the resourcequota admission plugin's `LimitedResources` scope-gating guarantee (an admission/policy-bypass class issue): a scope an administrator explicitly configured as "must always be covered by an enforcing ResourceQuota" can be bypassed by crafting a pod that only partially matches a multi-expression quota selector. Consequences depend on what the admin used the scope-gate for (e.g., requiring resource-limited pods for a privileged PriorityClass, or requiring explicit requests for BestEffort exclusion), but in all cases it is a control-plane logic bypass of an intended admission-time restriction, not merely a usage limit overage.

### Likelihood Explanation
Requires: (1) a cluster admin to have configured the resourcequota admission plugin's `LimitedResources` with `MatchScopes`, (2) a namespace `ResourceQuota` with a multi-expression `ScopeSelector`, and (3) an attacker with plain `create` on Pods in that namespace plus `get` on `resourcequotas` (both of which are common namespaced RBAC grants). No cluster-admin or node access is needed. This is deterministic and repeatable once those two admin-side conditions are met; it does not depend on any misconfiguration, only on legitimate use of a supported multi-expression `ScopeSelector` combined with `LimitedResources`.

### Recommendation
Change `restrictedScopes`/`UncoveredQuotaScopes` to reason in terms of whole quotas rather than individual expressions: only treat a `LimitedResources` scope as "covered" if there exists a quota whose full `ScopeSelector` (all expressions ANDed) matches the object (i.e., `evaluator.Matches` returned true for that quota, or equivalently gate the `restrictedScopes` accumulation on `match` at line 464 rather than appending `localRestrictedScopes` unconditionally at line 456).

### Proof of Concept
Table test in `staging/src/k8s.io/apiserver/pkg/admission/plugin/resourcequota/controller_test.go` (or `pkg/quota/v1/evaluator/core/pods_test.go`):
1. Configure `limited := []resourcequotaapi.LimitedResource{{APIGroup: "", Resource: "pods", MatchScopes: []corev1.ScopedResourceSelectorRequirement{{ScopeName: PriorityClass, Operator: In, Values: ["high"]}}}}`.
2. Create a `ResourceQuota` with `Spec.ScopeSelector.MatchExpressions = [{PriorityClass In [high]}, {BestEffort Exists}]` and `Status.Hard`/`Used` populated.
3. Build a Pod with `priorityClassName: high` and explicit CPU/memory requests (non-BestEffort).
4. Call `CheckRequest(quotas, attributes, podEvaluator, limited)`.
5. Assert current (buggy) behavior: no error is returned and quotas are unchanged, even though `evaluator.Matches` for that quota is false — proving the pod bypassed the `LimitedResources` scope requirement.
6. After the fix, assert `CheckRequest` returns `insufficient quota to match these scopes` for this input, matching the behavior when a single-expression selector is used.

### Citations

**File:** staging/src/k8s.io/apiserver/pkg/admission/plugin/resourcequota/controller.go (L388-399)
```go
func getMatchedLimitedScopes(evaluator quota.Evaluator, inputObject runtime.Object, limitedResources []resourcequotaapi.LimitedResource) ([]corev1.ScopedResourceSelectorRequirement, error) {
	scopes := []corev1.ScopedResourceSelectorRequirement{}
	for _, limitedResource := range limitedResources {
		matched, err := evaluator.MatchingScopes(inputObject, limitedResource.MatchScopes)
		if err != nil {
			klog.ErrorS(err, "Error while matching limited Scopes")
			return []corev1.ScopedResourceSelectorRequirement{}, err
		}
		scopes = append(scopes, matched...)
	}
	return scopes, nil
}
```

**File:** staging/src/k8s.io/apiserver/pkg/admission/plugin/resourcequota/controller.go (L449-456)
```go
	for i := range quotas {
		resourceQuota := quotas[i]
		scopeSelectors := getScopeSelectorsFromQuota(resourceQuota)
		localRestrictedScopes, err := evaluator.MatchingScopes(inputObject, scopeSelectors)
		if err != nil {
			return nil, fmt.Errorf("error matching scopes of quota %s, err: %v", resourceQuota.Name, err)
		}
		restrictedScopes = append(restrictedScopes, localRestrictedScopes...)
```

**File:** staging/src/k8s.io/apiserver/pkg/admission/plugin/resourcequota/controller.go (L458-476)
```go
		match, err := evaluator.Matches(&resourceQuota, inputObject)
		if err != nil {
			klog.ErrorS(err, "Error occurred while matching resource quota against input object",
				"resourceQuota", resourceQuota)
			return quotas, err
		}
		if !match {
			continue
		}

		hardResources := quota.ResourceNames(resourceQuota.Status.Hard)
		restrictedResources := evaluator.MatchingResources(hardResources)
		if err := evaluator.Constraints(restrictedResources, inputObject); err != nil {
			return nil, admission.NewForbidden(a, fmt.Errorf("failed quota: %s: %v", resourceQuota.Name, err))
		}
		if !hasUsageStats(&resourceQuota, restrictedResources) {
			return nil, admission.NewForbidden(a, fmt.Errorf("status unknown for quota: %s, resources: %s", resourceQuota.Name, prettyPrintResourceNames(restrictedResources)))
		}
		interestingQuotaIndexes = append(interestingQuotaIndexes, i)
```

**File:** staging/src/k8s.io/apiserver/pkg/admission/plugin/resourcequota/controller.go (L583-592)
```go
	// verify that for every scope that had limited access enabled
	// that there was a corresponding quota that covered it.
	// if not, we reject the request.
	scopesHasNoCoveringQuota, err := evaluator.UncoveredQuotaScopes(limitedScopes, restrictedScopes)
	if err != nil {
		return quotas, err
	}
	if len(scopesHasNoCoveringQuota) > 0 {
		return quotas, fmt.Errorf("insufficient quota to match these scopes: %v", scopesHasNoCoveringQuota)
	}
```

**File:** pkg/quota/v1/evaluator/core/pods.go (L224-237)
```go
// MatchingScopes takes the input specified list of scopes and pod object. Returns the set of scope selectors pod matches.
func (p *podEvaluator) MatchingScopes(item runtime.Object, scopeSelectors []corev1.ScopedResourceSelectorRequirement) ([]corev1.ScopedResourceSelectorRequirement, error) {
	matchedScopes := []corev1.ScopedResourceSelectorRequirement{}
	for _, selector := range scopeSelectors {
		match, err := podMatchesScopeFunc(selector, item)
		if err != nil {
			return []corev1.ScopedResourceSelectorRequirement{}, fmt.Errorf("error on matching scope %v: %v", selector, err)
		}
		if match {
			matchedScopes = append(matchedScopes, selector)
		}
	}
	return matchedScopes, nil
}
```

**File:** pkg/quota/v1/evaluator/core/pods.go (L241-257)
```go
func (p *podEvaluator) UncoveredQuotaScopes(limitedScopes []corev1.ScopedResourceSelectorRequirement, matchedQuotaScopes []corev1.ScopedResourceSelectorRequirement) ([]corev1.ScopedResourceSelectorRequirement, error) {
	uncoveredScopes := []corev1.ScopedResourceSelectorRequirement{}
	for _, selector := range limitedScopes {
		isCovered := false
		for _, matchedScopeSelector := range matchedQuotaScopes {
			if matchedScopeSelector.ScopeName == selector.ScopeName {
				isCovered = true
				break
			}
		}

		if !isCovered {
			uncoveredScopes = append(uncoveredScopes, selector)
		}
	}
	return uncoveredScopes, nil
}
```

**File:** staging/src/k8s.io/apiserver/pkg/quota/v1/generic/evaluator.go (L159-167)
```go
	// by default, no scopes matches all
	matchScope := true
	for _, scope := range getScopeSelectorsFromQuota(resourceQuota) {
		innerMatch, err := scopeFunc(scope, item)
		if err != nil {
			return false, err
		}
		matchScope = matchScope && innerMatch
	}
```
