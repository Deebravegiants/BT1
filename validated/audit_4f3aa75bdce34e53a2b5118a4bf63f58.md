Confirmed: `ValidateRole`/`ValidatePolicyRule` has no size limits on `APIGroups`/`Resources`/`Verbs`/`ResourceNames` lengths, only "required" (non-empty) checks. This confirms the ordering and lack of size caps that the question hypothesizes.

### Title
Escalation check runs before size-unbounded validation, allowing cartesian-product PolicyRule to trigger algorithmic blow-up in `BreakdownRule`/`Covers` prior to object validation - ([File: pkg/registry/rbac/role/policybased/storage.go])

### Summary
`Storage.Create` (and `Storage.Update`) in `pkg/registry/rbac/role/policybased/storage.go` invokes `ConfirmNoEscalationInternal` before delegating to `s.StandardStorage.Create`, which is where `strategy.Validate` (i.e., `ValidateRole`/`ValidateClusterRole`) actually runs. Since `ValidatePolicyRule` in `pkg/apis/rbac/validation/validation.go` only checks for non-empty `Verbs`/`APIGroups`/`Resources` and never bounds their lengths, a crafted `PolicyRule` with large `APIGroups`/`Resources`/`Verbs` arrays reaches the O(n³) nested loops in `BreakdownRule` (`staging/src/k8s.io/component-helpers/auth/rbac/validation/policy_comparator.go`) during the escalation check, before any size-based rejection could occur in validation (which itself has no size limit either).

### Finding Description
The reachable path is: an authenticated user with `create` permission on `roles`/`clusterroles` sends a `POST` with a `Role`/`ClusterRole` object whose `rules[]` contains a single `PolicyRule` with e.g. 1000 entries each in `APIGroups`, `Resources`, and `Verbs`. In `Storage.Create` [1](#0-0) , unless the caller already holds escalation rights, `ConfirmNoEscalationInternal` is called first, which calls `ConfirmNoEscalation` → `validation.Covers(ownerRules, rules)` [2](#0-1) , which in turn calls `BreakdownRule` for every servant rule [3](#0-2) . `BreakdownRule` performs a triple-nested loop over `APIGroups × Resources × Verbs` (further multiplied by `ResourceNames` if present) [4](#0-3) , producing up to `len(APIGroups) × len(Resources) × len(Verbs) × len(ResourceNames)` allocated `PolicyRule` structs. Only after this expensive/allocation-heavy step succeeds does control reach `s.StandardStorage.Create`, whose `BeforeCreate`/`rest.Storage` path eventually calls `ValidateRole`/`ValidateClusterRole` → `ValidatePolicyRule`, which never checks array lengths [5](#0-4) . So even validation, when it does run, would not have rejected the oversized rule anyway — there is no structural/size limit anywhere on the RBAC write path for `PolicyRule` array cardinalities.

### Impact Explanation
An attacker with only `create` rights on `roles`/`clusterroles` (a common namespace-scoped permission) can submit a single object whose JSON payload is modest in size (a few thousand short strings) but whose cartesian product explodes to billions of allocated struct instances inside `BreakdownRule`, consumed on every `Create`/`Update` call before the object is ever persisted. This causes CPU/memory exhaustion in the apiserver process handling the request (and potentially other concurrent requests sharing the same apiserver), i.e., a denial-of-service on the RBAC write path. This matches the Kubernetes bounty "Denial of Service" impact class; it does not on its own grant privilege escalation, since `Covers`/`ownerRightsCover` would still correctly reject the request if the attacker's actual permissions don't cover the requested rules (assuming the process survives the resource exhaustion).

### Likelihood Explanation
Minimal RBAC needed: `create` verb on `roles` or `clusterroles` (a routine permission for many operators/CI service accounts). No special feature gates are involved. The request is a single, ordinary `POST`/`PUT` — fully repeatable, and the multiplicative blow-up (`O(n³)` or worse with `ResourceNames`) means even array sizes in the hundreds to low thousands (well within any generic etcd/apiserver body-size limits of ~1.5–3MB, since string values can be very short) are sufficient to generate an enormous number of transient allocations.

### Recommendation
Add explicit size limits on `PolicyRule.APIGroups`, `Resources`, `Verbs`, `ResourceNames`, and `NonResourceURLs` in `ValidatePolicyRule` (`pkg/apis/rbac/validation/validation.go`), and enforce these limits (or a bound on the total cartesian-product size) *before* `ConfirmNoEscalationInternal`/`BreakdownRule` is invoked in `pkg/registry/rbac/role/policybased/storage.go` and the corresponding clusterrole storage, so that oversized rules are rejected with a cheap, bounded-time check prior to the expensive escalation computation.

### Proof of Concept
Table/unit test in `pkg/registry/rbac/role/policybased` (and clusterrole equivalent):
1. Construct a `rbac.Role` with one `rbac.PolicyRule` containing `APIGroups`, `Resources`, and `Verbs` slices each populated with 1000 unique short strings (e.g. `"g0".."g999"`, `"r0".."r999"`, `"v0".."v999"`), no `ResourceNames`.
2. Set up a context where the calling user does not hold escalation rights, so `ConfirmNoEscalationInternal` executes its full `Covers`/`BreakdownRule` path.
3. Call `Storage.Create` with this role and measure wall-clock time/memory, or directly call `validation.Covers(ownerRules, []rbacv1.PolicyRule{maliciousRule})`.
4. Assert either: (a) the call is rejected quickly (sub-millisecond) by a new size-limit check before `BreakdownRule` runs, or (b) if allowed to proceed, that CPU/memory stay within a defined bound (e.g., complete in <100ms and allocate <10MB) rather than the current unbounded `len(APIGroups)*len(Resources)*len(Verbs)` allocation (1,000,000,000 struct allocations for the 1000³ case), demonstrating the current code has no such bound.

### Citations

**File:** pkg/registry/rbac/role/policybased/storage.go (L67-78)
```go
func (s *Storage) Create(ctx context.Context, obj runtime.Object, createValidation rest.ValidateObjectFunc, options *metav1.CreateOptions) (runtime.Object, error) {
	if rbacregistry.EscalationAllowed(ctx) || rbacregistry.RoleEscalationAuthorized(ctx, s.authorizer) {
		return s.StandardStorage.Create(ctx, obj, createValidation, options)
	}

	role := obj.(*rbac.Role)
	rules := role.Rules
	if err := rbacregistryvalidation.ConfirmNoEscalationInternal(ctx, s.ruleResolver, rules); err != nil {
		return nil, errors.NewForbidden(groupResource, role.Name, err)
	}
	return s.StandardStorage.Create(ctx, obj, createValidation, options)
}
```

**File:** pkg/registry/rbac/validation/rule.go (L53-69)
```go
func ConfirmNoEscalation(ctx context.Context, ruleResolver AuthorizationRuleResolver, rules []rbacv1.PolicyRule) error {
	ruleResolutionErrors := []error{}

	user, ok := genericapirequest.UserFrom(ctx)
	if !ok {
		return fmt.Errorf("no user on context")
	}
	namespace, _ := genericapirequest.NamespaceFrom(ctx)

	ownerRules, err := ruleResolver.RulesFor(ctx, user, namespace)
	if err != nil {
		// As per AuthorizationRuleResolver contract, this may return a non fatal error with an incomplete list of policies. Log the error and continue.
		klog.V(1).Infof("non-fatal error getting local rules for %v: %v", user, err)
		ruleResolutionErrors = append(ruleResolutionErrors, err)
	}

	ownerRightsCover, missingRights := validation.Covers(ownerRules, rules)
```

**File:** staging/src/k8s.io/component-helpers/auth/rbac/validation/policy_comparator.go (L34-36)
```go
	for _, servantRule := range servantRules {
		subrules = append(subrules, BreakdownRule(servantRule)...)
	}
```

**File:** staging/src/k8s.io/component-helpers/auth/rbac/validation/policy_comparator.go (L58-84)
```go
func BreakdownRule(rule rbacv1.PolicyRule) []rbacv1.PolicyRule {
	subrules := []rbacv1.PolicyRule{}
	for _, group := range rule.APIGroups {
		for _, resource := range rule.Resources {
			for _, verb := range rule.Verbs {
				if len(rule.ResourceNames) > 0 {
					for _, resourceName := range rule.ResourceNames {
						subrules = append(subrules, rbacv1.PolicyRule{APIGroups: []string{group}, Resources: []string{resource}, Verbs: []string{verb}, ResourceNames: []string{resourceName}})
					}

				} else {
					subrules = append(subrules, rbacv1.PolicyRule{APIGroups: []string{group}, Resources: []string{resource}, Verbs: []string{verb}})
				}

			}
		}
	}

	// Non-resource URLs are unique because they only combine with verbs.
	for _, nonResourceURL := range rule.NonResourceURLs {
		for _, verb := range rule.Verbs {
			subrules = append(subrules, rbacv1.PolicyRule{NonResourceURLs: []string{nonResourceURL}, Verbs: []string{verb}})
		}
	}

	return subrules
}
```

**File:** pkg/apis/rbac/validation/validation.go (L104-127)
```go
func ValidatePolicyRule(rule rbac.PolicyRule, isNamespaced bool, fldPath *field.Path) field.ErrorList {
	allErrs := field.ErrorList{}
	if len(rule.Verbs) == 0 {
		allErrs = append(allErrs, field.Required(fldPath.Child("verbs"), "verbs must contain at least one value").MarkCoveredByDeclarative())
	}

	if len(rule.NonResourceURLs) > 0 {
		if isNamespaced {
			allErrs = append(allErrs, field.Invalid(fldPath.Child("nonResourceURLs"), rule.NonResourceURLs, "namespaced rules cannot apply to non-resource URLs"))
		}
		if len(rule.APIGroups) > 0 || len(rule.Resources) > 0 || len(rule.ResourceNames) > 0 {
			allErrs = append(allErrs, field.Invalid(fldPath.Child("nonResourceURLs"), rule.NonResourceURLs, "rules cannot apply to both regular resources and non-resource URLs"))
		}
		return allErrs
	}

	if len(rule.APIGroups) == 0 {
		allErrs = append(allErrs, field.Required(fldPath.Child("apiGroups"), "resource rules must supply at least one api group"))
	}
	if len(rule.Resources) == 0 {
		allErrs = append(allErrs, field.Required(fldPath.Child("resources"), "resource rules must supply at least one resource"))
	}
	return allErrs
}
```
