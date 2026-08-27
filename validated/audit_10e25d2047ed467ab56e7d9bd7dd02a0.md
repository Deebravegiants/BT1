### Title
Missing caller-identity check allows any user with `create` on `serviceaccounts/token` to mint a Node-bound token for an arbitrary Node - ([File: pkg/registry/core/serviceaccount/storage/token.go])

### Summary
`TokenREST.Create` handles `BoundObjectRef{Kind:"Node"}` by only checking the `ServiceAccountTokenNodeBinding` feature-gate and fetching the referenced Node object; it never verifies that the caller *is* that node. Because the RBAC verb `create` on `serviceaccounts/token` is already broadly granted (e.g. via the default `edit` ClusterRole, intended for Pod-bound tokens) and the NodeRestriction admission plugin only constrains callers that are already recognized node identities, an ordinary namespaced user can request and obtain a token whose claims embed an arbitrary node's identity.

### Finding Description
In `TokenREST.Create`, the `BoundObjectRef` switch statement handles the `Node` kind as follows: [1](#0-0) 
This branch only (1) checks the feature gate `ServiceAccountTokenNodeBinding`, and (2) does a plain `Get` of the named Node to populate `uid`/`node` for claims building — there is no authorization check tying the caller's identity to `ref.Name`. Compare this to the Pod case, where the code at least validates `name != pod.Spec.ServiceAccountName` (a serviceaccount-consistency check), but even that check has no analog for node ownership in the Node branch.

The comment in the RBAC bootstrap policy documents the *intended* enforcement split: "Use the Node authorization to limit a node to create tokens for service accounts running on that node" / "Use the NodeRestriction admission plugin to limit a node to create tokens bound to pods on that node." [2](#0-1) 
That design assumes the *only* principals holding `create` on `serviceaccounts/token` are node identities gated by the Node authorizer. But the default `edit` ClusterRole also grants this same verb/resource unconditionally to ordinary namespaced users, intended for Pod-bound token issuance: [3](#0-2) 
Since `serviceaccounts/token` `create` is a single undifferentiated verb (RBAC cannot distinguish `BoundObjectRef.Kind`), any principal with this permission (whether granted via `edit`, or any similarly-scoped custom role satisfying the audit's stated precondition) can supply `BoundObjectRef{Kind:"Node", Name:"victim-node"}`. The REST handler proceeds to mint a valid token embedding that Node's identity/claims via `token.Claims(...)`. [4](#0-3) 
NodeRestriction admission is scoped to callers already recognized as node identities (via `system:nodes` group / node user pattern); it does not run any node-name-matching logic for non-node callers, so it provides zero protection in this path.

### Impact Explanation
A minted TokenRequest with `BoundObjectRef{Kind:"Node"}` produces a JWT carrying node-identity claims for an arbitrary node the attacker doesn't control. Downstream consumers that trust node-bound token claims (e.g., systems using node identity for authorization/audit trust, credential-provider or node-scoped secret/configmap access decisions) can be tricked into treating the attacker as if they were that node — an authentication/token-forgery and identity-confusion class impact, matching Kubernetes bounty categories for authentication bypass / identity forgery.

### Likelihood Explanation
Feasibility is high given the stated preconditions: `ServiceAccountTokenNodeBinding` feature-gate enabled (default in current releases), and the caller holding only `create` on `serviceaccounts/token` — a permission already present in the built-in `edit` ClusterRole used pervasively for namespaced users. No node identity, no leaked kubelet credentials, and no admission bypass trick are required; the REST handler itself performs no ownership check for the Node kind.

### Recommendation
In `TokenREST.Create`'s Node case, add an explicit authorization check (mirroring the Pod-branch's serviceaccount-name consistency check) verifying the requesting user's identity corresponds to `ref.Name` (e.g., via the Node authorizer / node-identity matching used elsewhere for kubelet-scoped calls), and reject the request otherwise — rather than relying solely on the generic `serviceaccounts/token` RBAC verb plus a plugin that only guards already-recognized node callers.

### Proof of Concept
Integration test (extending `test/integration/auth/svcaccttoken_test.go`):
1. Start API server with `ServiceAccountTokenNodeBinding` enabled and RBAC authorization on.
2. Create an ordinary user/serviceaccount bound only to a ClusterRole granting `create` on `serviceaccounts/token` (or bind default `edit` role) in namespace `ns`, with no node credentials/identity.
3. Create Node object `victim-node` (simulating a node the attacker does not run).
4. As the ordinary user, call `POST /api/v1/namespaces/ns/serviceaccounts/<sa>/token` with `TokenRequest{Spec:{BoundObjectRef:{Kind:"Node",APIVersion:"v1",Name:"victim-node"}}}`.
5. Assert expectation: request should be rejected (403/Forbidden) because caller is not `victim-node`.
6. Actual (bug) result: request succeeds (200), returning a token; decode JWT and assert it embeds `victim-node`'s UID/name in claims, confirming unauthorized node-identity token issuance.

### Citations

**File:** pkg/registry/core/serviceaccount/storage/token.go (L211-221)
```go
		case gvk.Group == "" && gvk.Kind == "Node":
			if !utilfeature.DefaultFeatureGate.Enabled(features.ServiceAccountTokenNodeBinding) {
				return nil, errors.NewBadRequest(fmt.Sprintf("cannot bind token to a Node object as the %q feature-gate is disabled", features.ServiceAccountTokenNodeBinding))
			}
			newCtx := newContext(ctx, "nodes", ref.Name, "", gvk)
			nodeObj, err := r.nodes.Get(newCtx, ref.Name, &metav1.GetOptions{})
			if err != nil {
				return nil, err
			}
			node = nodeObj.(*api.Node)
			uid = node.UID
```

**File:** pkg/registry/core/serviceaccount/storage/token.go (L291-298)
```go
	sc, pc, err := token.Claims(*svcacct, pod, secret, node, validating, mutating, exp, warnAfter, req.Spec.Audiences, attestations)
	if err != nil {
		return nil, err
	}
	tokdata, err := r.issuer.GenerateToken(ctx, sc, pc)
	if err != nil {
		return nil, errors.NewInternalError(fmt.Errorf("failed to generate token: %v", err))
	}
```

**File:** plugin/pkg/auth/authorizer/rbac/bootstrappolicy/policy.go (L165-172)
```go
		rbacv1helpers.NewRule(Read...).Groups(legacyGroup).Resources("pods/attach", "pods/proxy", "pods/exec", "pods/portforward", "secrets", "services/proxy").RuleOrDie(),
		rbacv1helpers.NewRule("impersonate").Groups(legacyGroup).Resources("serviceaccounts").RuleOrDie(),

		rbacv1helpers.NewRule(Write...).Groups(legacyGroup).Resources("pods", "pods/attach", "pods/proxy", "pods/exec", "pods/portforward").RuleOrDie(),
		rbacv1helpers.NewRule("create").Groups(legacyGroup).Resources("pods/eviction").RuleOrDie(),
		rbacv1helpers.NewRule(Write...).Groups(legacyGroup).Resources("replicationcontrollers", "replicationcontrollers/scale", "serviceaccounts",
			"services", "services/proxy", "persistentvolumeclaims", "configmaps", "secrets").RuleOrDie(),
		rbacv1helpers.NewRule("create").Groups(legacyGroup).Resources("serviceaccounts/token").RuleOrDie(),
```

**File:** plugin/pkg/auth/authorizer/rbac/bootstrappolicy/policy.go (L266-268)
```go
		// Use the Node authorization to limit a node to create tokens for service accounts running on that node
		// Use the NodeRestriction admission plugin to limit a node to create tokens bound to pods on that node
		rbacv1helpers.NewRule("create").Groups(legacyGroup).Resources("serviceaccounts/token").RuleOrDie(),
```
