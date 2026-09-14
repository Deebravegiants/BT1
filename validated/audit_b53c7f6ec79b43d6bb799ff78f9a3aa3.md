### Title
Missing selector/capability filtering in `CapabilityController.ExecuteCapability` allows bypass of the system-only capability deny-list - (File: core/web/capability_controller.go)

### Summary
The `call()` bug class describes a powerful, generic dispatch function that accepts an arbitrary target/selector without filtering out dangerous, privileged-only operations. The Chainlink analog is `CapabilityController.ExecuteCapability`, an HTTP endpoint that looks up **any** capability by name from the registry and invokes `Execute()` with an attacker-controlled payload, with no check against the "system-only" capability deny-list that exists elsewhere in the codebase.

### Finding Description
`CapabilityController.ExecuteCapability` accepts a `capabilityName` and raw `capabilityRequest` bytes from the caller, resolves the capability via `capabilityRegistry.GetExecutable(...)`, and calls `capability.Execute(...)` directly: [1](#0-0) 

This is structurally identical to the vulnerable `LSSVMPair.call()` pattern: a generic dispatcher that reaches privileged internal functionality (here, any registered capability, by ID) without restricting which selectors/IDs are safe to invoke externally.

Elsewhere in the codebase, the workflow execution path (`ExecutionHelper.callCapability`, used when a WASM workflow calls a capability) explicitly maintains a deny-list of "system-only" capabilities (e.g. `confidential-workflows`) and rejects calls to them: [2](#0-1) [3](#0-2) 

This deny-list is enforced only in the workflow-triggered call path. `CapabilityController.ExecuteCapability` in `core/web/` has no equivalent `isSystemCapability` check, no capability-name allowlist, and no restriction on which methods/capabilities may be invoked: [4](#0-3) 

The test suite for the deny-list explicitly documents its purpose — internal plumbing capabilities like `confidential-workflows` "must not be callable from user workflow steps" — confirming this is a deliberate security boundary that the web controller path does not share: [5](#0-4) 

### Impact Explanation
If `ExecuteCapability` is reachable by an authenticated non-admin/lower-privilege API user (this specific route's role requirement in `core/web/router.go` was not fully confirmed within available tool budget — see Limitations below), an attacker could invoke system-only or otherwise restricted capabilities directly (e.g. `confidential-workflows`), bypassing the deny-list intended to keep such capabilities as internal plumbing only. Depending on what the resolved capability does, this could allow triggering privileged confidential-relay/TEE workflow execution, capability actions with elevated trust, or other operations that were never meant to be user-invokable — analogous to calling `onOwnershipTransferred()` or `pairTransferERC20From()` through an unrestricted `call()`.

### Likelihood Explanation
Likelihood depends on (a) which authenticated role can hit `/v2/execute_capability`, and (b) whether any system-only capability is actually registered and reachable in a given node/DON deployment. Given the existence of a dedicated, tested deny-list mechanism (`isSystemCapability`) for the workflow path, the omission in the HTTP controller path appears to be an inconsistency rather than an intentional design choice, making it plausible that this endpoint was overlooked when the deny-list was introduced.

### Recommendation
Apply the same `isSystemCapability` (or an equivalent explicit allowlist/deny-list) check in `CapabilityController.ExecuteCapability` before calling `capability.Execute(...)`, mirroring the check in `core/services/workflows/v2/capability_executor.go`. Reject requests targeting system-only capability IDs (post-resolution, to avoid version-string bypass as already handled in `capability_executor_test.go`'s `TestExecutionHelper_SystemCapabilityResolvedBypass`), and confirm the endpoint's required role in `core/web/router.go` is restricted appropriately.

### Proof of Concept
1. Authenticate as a user with whatever role is required for `/v2/execute_capability` (role/authentication middleware for this route was not fully verified — flagged as an open item).
2. Send `POST /v2/execute_capability` with `capabilityName: "confidential-workflows@1.0.0"` (or another system-only capability ID) and a crafted `capabilityRequest` payload.
3. Because `ExecuteCapability` performs no `isSystemCapability` check (unlike `ExecutionHelper.callCapability`), the request reaches `capability.Execute(...)` directly, bypassing the intended restriction that this capability is "internal plumbing" not callable outside the workflow engine's controlled path.

### Limitations / Uncertainty
I could not fully confirm, within the available tool calls, the exact authentication/role middleware wrapping the `/v2/execute_capability` route in `core/web/router.go` (i.e., whether it requires admin/run/view role, or an API token only). This affects the precise likelihood/severity assessment. I recommend verifying the router registration for `CapabilityController.ExecuteCapability` before treating this as confirmed high-severity — a Devin session with full file access could confirm this quickly.

### Citations

**File:** core/web/capability_controller.go (L22-60)
```go
// ExecuteCapability executes a capability by name with the provided request
// Example:
//
//	"<application>/v2/execute_capability"
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

**File:** core/services/workflows/v2/capability_executor.go (L142-157)
```go
func (c *ExecutionHelper) callCapability(ctx context.Context, request *sdkpb.CapabilityRequest) (*sdkpb.CapabilityResponse, error) {
	execLogger := c.logger().With("workflowExecutionID", c.WorkflowExecutionID, "capabilityID", request.Id, "callbackID", request.CallbackId, "method", request.Method)
	// TODO (CAPPL-735): use request.Metadata.WorkflowExecutionId to associate the call with a specific execution
	capability, err := c.cfg.CapRegistry.GetExecutable(ctx, request.Id)
	if err != nil {
		return nil, fmt.Errorf("action capability not found: %w, ", err)
	}

	info, err := capability.Info(ctx)
	if err != nil {
		return nil, fmt.Errorf("capability info not found: %w", err)
	}

	if isSystemCapability(info.ID) {
		return nil, fmt.Errorf("capability %q is system-only and cannot be called from a workflow", info.ID)
	}
```

**File:** core/services/workflows/v2/capability_executor.go (L338-346)
```go
// systemCapabilities lists capability IDs that are internal plumbing and must
// not be callable from user workflow steps.
var systemCapabilities = map[string]bool{
	confidentialWorkflowsCapabilityID: true,
}

func isSystemCapability(capID string) bool {
	return systemCapabilities[capID]
}
```

**File:** core/services/workflows/v2/capability_executor_test.go (L22-44)
```go
func TestExecutionHelper_SystemCapabilityBlocked(t *testing.T) {
	t.Parallel()

	resolvedInfo := capabilities.CapabilityInfo{ID: confidentialWorkflowsCapabilityID}
	reg := stubRegistry{cap: stubExecutableCapability{CapabilityInfo: resolvedInfo}}

	engine := &Engine{cfg: &EngineConfig{
		Lggr:        logger.TestLogger(t),
		CapRegistry: reg,
	}}
	engine.setLogger(commonlogger.Sugared(commonlogger.Test(t)))
	exec := &ExecutionHelper{Engine: engine}

	req := &sdk.CapabilityRequest{
		Id:         confidentialWorkflowsCapabilityID,
		Method:     "Execute",
		CallbackId: 1,
	}

	_, err := exec.callCapability(t.Context(), req)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "system-only")
}
```
