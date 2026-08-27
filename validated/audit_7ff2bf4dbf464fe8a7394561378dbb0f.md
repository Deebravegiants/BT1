### Title
TokenREST.Create Node BoundObjectRef branch allows binding a token to an arbitrary Node without verifying any relationship between the caller/SA and that node - ([File: pkg/registry/core/serviceaccount/storage/token.go])

### Summary
When `req.Spec.BoundObjectRef.Kind == "Node"`, `TokenREST.Create` only checks that the `ServiceAccountTokenNodeBinding` feature gate is enabled and that the named `Node` object exists (and optionally that its UID matches), then embeds that node's name/UID as `kubernetes.io/node` claims in the minted SA token. There is no authorization or ownership check tying the requesting principal (or the target ServiceAccount) to that specific node, unlike the `Pod` case which at least requires the pod to be running under the same SA, and unlike node-identity callers who are restricted by the `NodeRestriction` admission plugin to Pod-only bindings.

### Finding Description
In `pkg/registry/core/serviceaccount/storage/token.go`, the `Node` case of the `BoundObjectRef` switch is: [1](#0-0) 

This performs `r.nodes.Get(...)` (an in-process object fetch, not a separate authorization decision) and sets `uid = node.UID`. Compare this to the `Pod` case, which enforces `name != pod.Spec.ServiceAccountName` as a consistency check binding token identity to pod identity: [2](#0-1) 

No equivalent check exists for `Node` — any caller authorized only for `create` on `serviceaccounts/token` for a given SA name can supply `BoundObjectRef{Kind: Node, Name: <any-existing-node>}` and receive a token whose private claims embed that node's name/UID: [3](#0-2) 

On token validation, this claim surfaces as `authentication.kubernetes.io/node-name` / `node-uid` in the authenticated `user.Info` extra fields: [4](#0-3) 

Critically, in-tree consumers treat this `node-name` extra value as proof that the SA is actually running on that node, and use it to scope write access per-node (e.g. the DRA kubelet-plugin `ValidatingAdmissionPolicy` restricting `resourceslices` writes to the node matching the caller's `node-name` claim, and the analogous per-node ConfigMap policy): [5](#0-4) [6](#0-5) 

The intended path to obtain this claim legitimately is via a Pod scheduled on that node (`ServiceAccountTokenPodNodeInfo`), where `node.Name` is derived from `pod.Spec.NodeName` — a value the requester cannot arbitrarily choose since scheduling is controlled by the scheduler/kubelet, not the requester: [7](#0-6) 

The direct `Node` BoundObjectRef path bypasses this constraint entirely: whoever can create a token for the target SA can pick any existing node name to embed as the trusted `node-name` claim. The `NodeRestriction` admission plugin, which forces genuine node/kubelet identities to bind only to Pods (preventing a compromised node from spoofing another node's binding), does not apply here because it only inspects requests attributed to node users; a non-node caller with `create` on `serviceaccounts/token` is not subject to that restriction: [8](#0-7) 

### Impact Explanation
Any principal (user, SA, controller) that already holds `create` on `serviceaccounts/token` for a specific target ServiceAccount — and that target SA is consumed by any policy/mechanism trusting the `authentication.kubernetes.io/node-name` extra claim as proof-of-node-identity (as demonstrated by the shipped DRA kubelet-plugin and per-node-update example policies) — can forge that claim to reference an arbitrary Node object rather than the node it is legitimately scheduled/running on. This breaks the node-scoping invariant those consumers rely on and enables cross-node privilege escalation/unauthorized writes scoped to victim nodes (e.g., forging `resourceslices` writes for a node the caller does not control). This maps to a control-plane RBAC/authorizer-bypass and identity-forgery class of impact.

### Likelihood Explanation
Exploitability requires the attacker to already hold `create` on `serviceaccounts/token` for a specific SA that is consumed by a node-scoped-trust mechanism (such as the DRA kubelet-plugin SA), plus knowledge/`get` of an arbitrary Node object name+UID (node names/UIDs are commonly readable cluster-wide). This is a realistic, narrowly-scoped but repeatable RBAC configuration seen in-tree (e.g. the example DRA kubelet-plugin RoleBinding grants exactly this `serviceaccounts/token` create permission scoped to its own SA). No node/kubelet compromise, admin access, or webhook control is required — only the documented minimal RBAC.

### Recommendation
For the `Node` BoundObjectRef branch, require an explicit authorization check (similar to `authorizeAdmissionWebhookAuthnTokenRequest`) verifying the requester/SA is actually authorized to bind a token to that specific Node object, rather than relying solely on the generic `create serviceaccounts/token` RBAC grant. Alternatively, restrict direct `Node`-kind `BoundObjectRef` requests to callers with node identity (as already enforced for Pod-bound tokens issued by nodes) and continue deriving node claims for all other callers strictly from `pod.Spec.NodeName` of a Pod the requester is authorized to bind to, never from a user-supplied arbitrary node reference.

### Proof of Concept
Integration test (extending `test/integration/auth/svcaccttoken_test.go` patterns):
1. Grant a test SA `create` on `serviceaccounts/token` for target SA `dra-kubelet-plugin-service-account` (mirroring `plugin-permissions.yaml`), and apply the `resourceslices-policy-dra-kubelet-plugin` ValidatingAdmissionPolicy from `test/e2e/dra/test-driver/deploy/example/plugin-permissions.yaml`.
2. Create two Node objects, `node-legit` (where the plugin pod actually runs) and `node-victim` (a node the SA has no relationship to).
3. As the low-privileged caller (only holding `create serviceaccounts/token` for the target SA, no node/kubelet identity), call `CreateToken` with `BoundObjectRef{Kind: "Node", Name: "node-victim", UID: node-victim.UID}`.
4. Assert the call succeeds (`TokenREST.Create` returns a token) and that a `TokenReview`/`SelfSubjectReview` of the resulting token shows `authentication.kubernetes.io/node-name = node-victim`.
5. Using that token, attempt to create/patch a `ResourceSlice` with `spec.nodeName = node-victim`; assert the `ValidatingAdmissionPolicy` allows it (expected: allowed, demonstrating escalation to write resources scoped to `node-victim` despite the SA/pod never running there) — expected assertion: request succeeds where it should be denied since the caller has no genuine relationship to `node-victim`.

### Citations

**File:** pkg/registry/core/serviceaccount/storage/token.go (L178-188)
```go
		case gvk.Group == "" && gvk.Kind == "Pod":
			newCtx := newContext(ctx, "pods", ref.Name, namespace, gvk)
			podObj, err := r.pods.Get(newCtx, ref.Name, &metav1.GetOptions{})
			if err != nil {
				return nil, err
			}
			pod = podObj.(*api.Pod)
			if name != pod.Spec.ServiceAccountName {
				return nil, errors.NewBadRequest(fmt.Sprintf("cannot bind token for serviceaccount %q to pod running with different serviceaccount name.", name))
			}
			uid = pod.UID
```

**File:** pkg/registry/core/serviceaccount/storage/token.go (L189-209)
```go
			if utilfeature.DefaultFeatureGate.Enabled(features.ServiceAccountTokenPodNodeInfo) {
				if nodeName := pod.Spec.NodeName; nodeName != "" {
					newCtx := newContext(ctx, "nodes", nodeName, "", api.SchemeGroupVersion.WithKind("Node"))
					// set ResourceVersion=0 to allow this to be read/served from the apiservers watch cache
					nodeObj, err := r.nodes.Get(newCtx, nodeName, &metav1.GetOptions{ResourceVersion: "0"})
					if err != nil {
						nodeObj, err = r.nodes.Get(newCtx, nodeName, &metav1.GetOptions{}) // fallback to a live lookup on any error
					}
					switch {
					case errors.IsNotFound(err):
						// if the referenced Node object does not exist, we still embed just the pod name into the
						// claims so that clients still have some indication of what node a pod is assigned to when
						// inspecting a token (even if the UID is not present).
						klog.V(4).ErrorS(err, "failed fetching node for pod", "pod", klog.KObj(pod), "podUID", pod.UID, "nodeName", nodeName)
						node = &api.Node{ObjectMeta: metav1.ObjectMeta{Name: nodeName}}
					case err != nil:
						return nil, errors.NewInternalError(err)
					default:
						node = nodeObj.(*api.Node)
					}
				}
```

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

**File:** pkg/serviceaccount/claims.go (L123-130)
```go
	case node != nil:
		if !utilfeature.DefaultFeatureGate.Enabled(features.ServiceAccountTokenNodeBinding) {
			return nil, nil, fmt.Errorf("token bound to Node object requested, but %q feature gate is disabled", features.ServiceAccountTokenNodeBinding)
		}
		pc.Kubernetes.Node = &ref{
			Name: node.Name,
			UID:  string(node.UID),
		}
```

**File:** staging/src/k8s.io/apiserver/pkg/authentication/serviceaccount/util.go (L178-187)
```go
	if sa.NodeName != "" {
		if info.Extra == nil {
			info.Extra = make(map[string][]string)
		}
		info.Extra[NodeNameKey] = []string{sa.NodeName}
		// node UID is optional and will only be set if the node name is set
		if sa.NodeUID != "" {
			info.Extra[NodeUIDKey] = []string{sa.NodeUID}
		}
	}
```

**File:** test/e2e/dra/test-driver/deploy/example/plugin-permissions.yaml (L60-78)
```yaml
  matchConditions:
  - name: isRestrictedUser
    expression: >-
      request.userInfo.username == "system:serviceaccount:dra-kubelet-plugin-namespace:dra-kubelet-plugin-service-account"
  variables:
  - name: userNodeName
    expression: >-
      request.userInfo.extra[?'authentication.kubernetes.io/node-name'][0].orValue('')
  - name: objectNodeName
    expression: >-
      (request.operation == "DELETE" ? oldObject : object).spec.?nodeName.orValue("")
  validations:
  - expression: variables.userNodeName != ""
    message: >-
      no node association found for user, this user must run in a pod on a node and ServiceAccountTokenPodNodeInfo must be enabled
  - expression: variables.userNodeName == variables.objectNodeName
    messageExpression: >-
      "this user running on node '"+variables.userNodeName+"' may not modify " +
      (variables.objectNodeName == "" ?"cluster resourceslices" : "resourceslices on node '"+variables.objectNodeName+"'")
```

**File:** test/e2e/auth/e2edata/per_node_validatingadmissionpolicy.yaml (L13-31)
```yaml
  matchConditions:
  - name: isRestrictedUser
    # e2e-ns gets replaced with the tests's namespace when running the E2E test.
    expression: >-
      request.userInfo.username == "system:serviceaccount:e2e-ns:default"
  variables:
  - name: userNodeName
    expression: >-
      request.userInfo.extra[?'authentication.kubernetes.io/node-name'][0].orValue('')
  - name: objectNodeName
    expression: >-
      (request.operation == 'DELETE' ? oldObject : object).?metadata.name.orValue('')
  validations:
  - expression: variables.userNodeName != ""
    message: >-
      no node association found for user, this user must run in a pod on a node and ServiceAccountTokenPodNodeInfo must be enabled
  - expression: variables.userNodeName == variables.objectNodeName
    messageExpression: >-
      "this user running on node '"+variables.userNodeName+"' may not modify ConfigMap '" + variables.objectNodeName +
```

**File:** plugin/pkg/admission/noderestriction/admission.go (L684-692)
```go
	// TokenRequests from a node must have a pod binding. That pod must be
	// scheduled on the node.
	ref := tr.Spec.BoundObjectRef
	if ref == nil ||
		ref.APIVersion != "v1" ||
		ref.Kind != "Pod" ||
		ref.Name == "" {
		return admission.NewForbidden(a, fmt.Errorf("node requested token not bound to a pod"))
	}
```
