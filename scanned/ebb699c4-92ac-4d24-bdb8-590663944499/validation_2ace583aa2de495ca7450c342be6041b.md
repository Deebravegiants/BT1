Based on my investigation, I found a genuine analog to the ScadaLTS bug class: an authenticated-but-under-privileged user reaching a method that lacks the request-specific authorization checks enforced elsewhere in the same subsystem.

### Title
Unauthorized arbitrary capability execution via `/v2/execute_capability` bypasses capability-level authorization - (File: `core/web/capability_controller.go`)

### Summary
`CapabilityController.ExecuteCapability` lets any session/API-token authenticated user holding the lowest non-view role ("Run") invoke **any** capability registered in the node's `CapabilitiesRegistry` by name, with a fully attacker-controlled `CapabilityRequest` payload, bypassing the request-level authorization (ownership/allowlist/DON-binding) checks that other capability-invocation paths in the same codebase enforce.

### Finding Description
The route is wired as: [1](#0-0) 

which registers `POST /v2/execute_capability` behind `auth.RequiresRunRole`, i.e. any authenticated user whose role is not `UserRoleView` — the minimum privileged, effectively "read/execute" role, analogous to the low-privilege role in the ScadaLTS report: [2](#0-1) 

The handler itself performs no additional authorization beyond the role check — it looks up an arbitrary named capability from the global registry and executes it directly with the caller-supplied protobuf request: [3](#0-2) 

This stands in contrast to every other capability-invocation path in the codebase, which layers method/owner/allowlist authorization before execution — e.g. the vault gateway handler's `AllowListBasedAuth.AuthorizeRequest` (digest + owner + expiry validation) before any secret operation is allowed: [4](#0-3) 

and the P2P remote-execution path's DON-binding check that prevents a caller from spoofing `WorkflowDonID`: [5](#0-4) 

`ExecuteCapability` has none of this: the `Metadata.WorkflowID`/`WorkflowOwner` in the request are attacker-supplied and never validated against the caller's identity, and the capability name/target is entirely attacker-chosen from the full registry.

### Impact Explanation
Because any capability registered on the node (which can include write/target capabilities such as web API targets, on-chain transaction/target capabilities, or other action capabilities) can be invoked directly and does not go through the normal workflow-engine/DON authorization boundary, a low-privileged "Run"-role user can trigger capability actions (e.g., HTTP requests to internal endpoints via a target capability, or job/fund-relevant actions if such a capability is registered) that they would not otherwise be authorized to trigger through the standard job/workflow lifecycle. This mirrors the "unauthorized job run" class explicitly called out as acceptable impact.

### Likelihood Explanation
The route requires only session or API-token authentication plus the "Run" role — the lowest privileged role capable of calling any authenticated endpoint besides pure "View." No workflow ownership, allowlisting, or DON membership check gates the call, unlike comparable authenticated capability paths elsewhere in the codebase.

### Recommendation
Add request-level authorization to `ExecuteCapability` mirroring the vault/DON patterns: validate that the caller (workflow owner / DON identity) is authorized for the specific capability and metadata in the request, or restrict this endpoint's capability set to those explicitly safe for direct invocation, rather than allowing arbitrary lookup+execute against the full registry.

### Proof of Concept
1. Authenticate as a user with `Run` role (or lowest role above `View`) via session cookie or API token.
2. `POST /v2/execute_capability` with body `{"capabilityName": "<any-registered-capability>", "capabilityRequest": <base64/binary-marshaled CapabilityRequest with attacker-chosen Metadata.WorkflowID/WorkflowOwner and Inputs/Config>}`.
3. The server resolves and executes the capability directly (`core/web/capability_controller.go:44-56`), with no ownership/allowlist check on the supplied metadata, and returns the capability's response.

**Caveat / uncertainty:** I could not verify within the given tool budget whether this route is gated to non-production builds — the registration is wrapped in `if build.IsDev() { ... }` in `core/web/router.go:304-307`, and I was unable to locate/confirm the definition of `build.IsDev()` (no matches found in indexed content) to determine whether this evaluates to `false` in released production binaries. If `IsDev()` is always false in production releases, this endpoint would not be reachable outside development builds, which would significantly reduce or eliminate the real-world impact of this finding. This should be confirmed with a full repository checkout before treating this as production-exploitable.

### Citations

**File:** core/web/router.go (L304-307)
```go
		if build.IsDev() {
			capContr := CapabilityController{app}
			authv2.POST("/execute_capability", auth.RequiresRunRole(capContr.ExecuteCapability))
		}
```

**File:** core/web/auth/auth.go (L198-215)
```go
// RequiresRunRole extracts the user object from the context, and asserts the user's role is at least
// 'run'
func RequiresRunRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}
```

**File:** core/web/capability_controller.go (L26-60)
```go
func (cc *CapabilityController) ExecuteCapability(c *gin.Context) {
	body := c.Request.Body
	if body == nil {
		jsonAPIError(c, http.StatusBadRequest, errors.New("missing request body"))
		return
	}

	capabilityRegistry := cc.App.GetCapabilitiesRegistry()
	if capabilityRegistry == nil {
		jsonAPIError(c, http.StatusInternalServerError, errors.New("capability registry not initialized"))
		return
	}
	var capabilityRequestOuter CapabilityRequestOuter
	if err := c.BindJSON(&capabilityRequestOuter); err != nil {
		jsonAPIError(c, http.StatusBadRequest, err)
		return
	}

	capability, err := capabilityRegistry.GetExecutable(c.Request.Context(), capabilityRequestOuter.CapabilityName)
	if err != nil {
		jsonAPIError(c, http.StatusNotFound, err)
		return
	}

	capabilityRequest, err := pb.UnmarshalCapabilityRequest(capabilityRequestOuter.CapabilityRequest)
	if err != nil {
		jsonAPIError(c, http.StatusBadRequest, err)
		return
	}

	resp, err := capability.Execute(c.Request.Context(), capabilityRequest)
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L32-77)
```go
// AuthorizeRequest authorizes a request using AllowListBasedAuth.
// It does NOT check if the request method is allowed.
func (r *allowListBasedAuth) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	r.lggr.Debugw("AllowListBasedAuth authorizing request", "method", req.Method, "requestID", req.ID)
	requestDigest, err := req.Digest()
	if err != nil {
		r.lggr.Debugw("AllowListBasedAuth failed to create digest", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, err
	}
	requestDigestBytes, err := hex.DecodeString(requestDigest)
	if err != nil {
		r.lggr.Debugw("AllowListBasedAuth failed to decode digest", "method", req.Method, "requestID", req.ID, "requestDigest", requestDigest, "error", err)
		return nil, err
	}
	requestDigestBytes32 := [32]byte(requestDigestBytes)
	if r.workflowRegistrySyncer == nil {
		r.lggr.Errorw("AllowListBasedAuth workflowRegistrySyncer is nil", "method", req.Method, "requestID", req.ID)
		return nil, errors.New("internal error: workflowRegistrySyncer is nil")
	}
	allowlistedRequest, allowedRequestsStrs, err := r.findAllowlistedItemWithRetry(ctx, req, requestDigest, requestDigestBytes32)
	if err != nil {
		return nil, err
	}
	if allowlistedRequest == nil {
		r.lggr.Debugw("AllowListBasedAuth request digest not allowlisted",
			"method", req.Method,
			"requestID", req.ID,
			"digestHexStr", requestDigest,
			"allowedRequestsStrs", allowedRequestsStrs)
		return nil, errors.New("request not allowlisted")
	}

	if time.Now().UTC().Unix() > int64(allowlistedRequest.ExpiryTimestamp) {
		authorizedRequestStr := string(allowlistedRequest.RequestDigest[:])
		r.lggr.Debugw("AllowListBasedAuth authorization expired", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", authorizedRequestStr, "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
		return nil, errors.New("request authorization expired")
	}

	digestKey := string(allowlistedRequest.RequestDigest[:])
	r.lggr.Debugw("AllowListBasedAuth authorization succeeded", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", digestKey, "owner", allowlistedRequest.Owner.Hex(), "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
	return &AuthResult{
		workflowOwner: allowlistedRequest.Owner.Hex(),
		digest:        digestKey,
		expiresAt:     int64(allowlistedRequest.ExpiryTimestamp),
	}, nil
}
```

**File:** core/capabilities/remote/executable/request/server_request.go (L395-409)
```go
	// When enabled, bind the caller-supplied WorkflowDonID to the authenticated
	// calling DON so it cannot be spoofed. All F+1 aggregated requests share this
	// payload (WorkflowDonID is part of the request hash), so a single check here
	// covers the quorum. The gate is guaranteed non-nil by NewServerRequest.
	enabled, gerr := workflowDONBindingGate.Limit(ctx)
	if gerr != nil {
		lggr.Errorw("failed to evaluate workflow DON binding gate", "err", gerr)
		return nil, errors.New("failed to evaluate workflow DON binding gate")
	}
	if enabled && capabilityRequest.Metadata.WorkflowDonID != callingDonID {
		lggr.Errorw("workflow DON ID in request metadata does not match calling DON",
			"metadataWorkflowDonID", capabilityRequest.Metadata.WorkflowDonID, "callingDonID", callingDonID)
		return nil, fmt.Errorf("workflow DON ID %d in request metadata does not match calling DON ID %d",
			capabilityRequest.Metadata.WorkflowDonID, callingDonID)
	}
```
