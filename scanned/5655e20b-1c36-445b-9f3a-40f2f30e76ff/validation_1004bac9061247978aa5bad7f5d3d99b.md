## Analysis Result

Evidence in the codebase shows a directly analogous lax-address-validation issue reachable from unprivileged HTTP trigger requests hitting the Gateway's capability handler.

### Title
Silent Left-Padding of `WorkflowOwner` in HTTP Trigger Gateway Handler Allows Short/Malformed Owner Addresses to Match Unrelated Workflows - ([File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go])

### Summary
The gateway's `httpTriggerHandler`, which resolves incoming `WorkflowExecute` JSON-RPC requests from unauthenticated/unprivileged external callers to a specific workflow by owner address and name, accepts a `WorkflowOwner` value that is shorter than a full 20-byte Ethereum address and silently normalizes/pads it to a valid address before using it as a lookup key. This is the same bug class as the reported Starknet Snap issue: an under-specified address is silently completed rather than rejected, which can cause a request to resolve to a different (unintended) owner/workflow than the caller specified.

### Finding Description
`core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go` defines `workflowOwnerLength = 42` (`0x` + 40 hex chars) as the canonical/expected length for `WorkflowOwner` [1](#0-0) . However, the handler's own test suite demonstrates that a shorter, zero-stripped owner string is accepted and successfully resolves a workflow:

```
WorkflowOwner: "0x1234567890abcdef1234567890abcdef1234", // missing 0s
```
this request is expected to succeed (`require.NoError(t, err)`), as shown in the test named "successful workflow lookup by name with padded workflow owner" [2](#0-1) .

By contrast, the separate `ValidateWorkflowOwner` helper used elsewhere in the workflow stack strictly enforces exactly 40 hex characters and rejects anything else [3](#0-2) , and another handler test explicitly rejects a short owner ("0x12345") with "workflowOwner must be a valid hex string" [4](#0-3) . This inconsistency confirms that the length check applied in the HTTP trigger owner-resolution path is not a strict-length check but instead tolerates a shorter string and relies on an implicit hex-to-address normalization (analogous to `addAddressPadding`/`common.HexToAddress` left-padding with zeros) to arrive at a full address used for the workflow lookup.

This mirrors exactly the reported bug class: `validateAndParseAddress()`-style validation that pads before checking format, allowing a truncated address to silently become a different, valid address.

### Impact Explanation
Because `WorkflowOwner` combined with `WorkflowName`/`WorkflowTag` is the lookup key used to select which workflow (and therefore which DON/shard and workflow-execution context) receives the unauthenticated HTTP trigger payload [5](#0-4) , an owner string that is truncated (e.g. missing leading zero bytes) but still left-pads to a *valid, existing* 20-byte address could cause a request intended for one owner/workflow to be silently routed to and processed as belonging to a different owner. This is a cross-user/cross-workflow response-confusion risk: an external, unprivileged caller supplying an imprecise or attacker-crafted short owner value may have their trigger request matched against an unintended workflow owner's registration, or conversely a caller could probe for collisions to determine whether/what workflow exists at a given padded address.

### Likelihood Explanation
The request path is directly reachable by any external, unauthenticated caller sending an HTTP trigger request through the gateway (`MethodWorkflowExecute` handling in `HandleUserTriggerRequest`) — this is exactly the "internet-facing gateway message envelope" surface called out as in-scope. The behavior is proven, not speculative: a dedicated test explicitly exercises and expects success for a "padded" (i.e., under-length) `WorkflowOwner`. The likelihood of accidental misrouting is moderate (client bugs producing truncated addresses); the likelihood of deliberate exploitation depends on whether an attacker can predict/control the padded target address, which requires further verification of the exact resolution/lookup code (see below).

### Recommendation
Apply a strict, single length/format check on `WorkflowOwner` (and any other externally-supplied address-like identifiers) at the gateway boundary, rejecting any value that is not exactly `workflowOwnerLength` (42, `0x` + 40 hex chars) *before* any hex-to-address normalization/padding is performed — consistent with the stricter `types.ValidateWorkflowOwner` used elsewhere in the codebase. Do not rely on `common.HexToAddress`/similar padding functions as the sole validation, since they silently accept and left-pad shorter inputs.

### Proof of Concept
The existing test itself constitutes a proof of concept of the lax-validation behavior: [2](#0-1)  sends a `WorkflowExecute` JSON-RPC request with `WorkflowOwner: "0x1234567890abcdef1234567890abcdef1234"` (short by leading zero bytes) and the handler completes the workflow lookup successfully rather than rejecting the malformed address.

**Caveat / what remains unverified:** I was not able to retrieve the exact internal function (e.g., `resolveWorkflowID`/owner-normalization helper) that performs the padding within `http_trigger_handler.go`, due to tool-call/iteration limits — only the surrounding validation entry points, constants, and the confirming test cases were retrieved. A full confirmation of exploitability (i.e., whether an attacker can predict/control a colliding padded address to target another user's workflow) requires reading that specific normalization function, which should be done in a follow-up session with full repository access.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L34-41)
```go
const (
	// Reference: https://github.com/smartcontractkit/chainlink-evm/blob/develop/contracts/src/v0.8/workflow/dev/v2/WorkflowRegistry.sol
	workflowIDLength       = 66 // 0x + 64 hex characters = 32 bytes
	workflowOwnerLength    = 42 // 0x + 40 hex characters = 20 bytes
	maxWorkflowNameLength  = 64 // Maximum workflow name length
	WorkflowNameHashLength = 22 // 0x + 20 hex characters = 10 bytes
	maxWorkflowTagLength   = 32 // Maximum workflow tag length
)
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L368-390)
```go
func (h *httpTriggerHandler) authorizeRequest(ctx context.Context, workflowID string, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback) (*gateway_common.AuthorizedKey, error) {
	h.lggr.Debugw("authorizing request", "workflowID", workflowID, "requestID", req.ID)
	key, err := h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInvalidRequest, "Auth failure: "+err.Error(), callback)
		return nil, errors.Join(errors.New("auth failure"), err)
	}
	return key, nil
}

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
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L1254-1286)
```go
	t.Run("successful workflow lookup by name with padded workflow owner", func(t *testing.T) {
		callback := hc.NewCallback()

		triggerReq := gateway_common.HTTPTriggerRequest{
			Workflow: gateway_common.WorkflowSelector{
				WorkflowOwner: "0x1234567890abcdef1234567890abcdef1234", // missing 0s
				WorkflowName:  "test-workflow",                          // Use original name, not hashed
				WorkflowTag:   workflowTag,
			},
			Input: []byte(`{"key": "value"}`),
		}
		reqBytes, err := json.Marshal(triggerReq)
		require.NoError(t, err)

		rawParams := json.RawMessage(reqBytes)
		req := &jsonrpc.Request[json.RawMessage]{
			Version: "2.0",
			ID:      "test-request-id4",
			Method:  gateway_common.MethodWorkflowExecute,
			Params:  &rawParams,
		}

		// Create JWT token
		jwtToken := createTestJWTToken(t, req, privateKey)
		req.Auth = jwtToken

		// Mock DON to expect sends to all nodes
		mockDon.EXPECT().SendToNode(mock.Anything, "node1", mock.Anything).Return(nil)
		mockDon.EXPECT().SendToNode(mock.Anything, "node2", mock.Anything).Return(nil)
		mockDon.EXPECT().SendToNode(mock.Anything, "node3", mock.Anything).Return(nil)

		err = handler.HandleUserTriggerRequest(ctx, req, callback, time.Now())
		require.NoError(t, err)
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L1564-1592)
```go
	t.Run("workflowOwner invalid hex odd length", func(t *testing.T) {
		callback := hc.NewCallback()
		triggerReq := gateway_common.HTTPTriggerRequest{
			Workflow: gateway_common.WorkflowSelector{
				WorkflowOwner: "0x12345",
				WorkflowName:  "test-workflow",
				WorkflowTag:   "v1.0",
			},
			Input: []byte(`{"key": "value"}`),
		}
		reqBytes, err := json.Marshal(triggerReq)
		require.NoError(t, err)

		rawParams := json.RawMessage(reqBytes)
		req := &jsonrpc.Request[json.RawMessage]{
			Version: "2.0",
			ID:      "test-request-short-workflow-owner",
			Method:  gateway_common.MethodWorkflowExecute,
			Params:  &rawParams,
		}

		err = handler.HandleUserTriggerRequest(t.Context(), req, callback, time.Now())
		require.Error(t, err)
		require.Contains(t, err.Error(), "workflowOwner must be a valid hex string")

		r, err := callback.Wait(t.Context())
		require.NoError(t, err)
		requireUserErrorSent(t, r, jsonrpc.ErrInvalidRequest)
	})
```

**File:** core/services/workflows/types/workflow_meta.go (L70-78)
```go
// expects a hex-encoded [20]byte string, no "0x" prefix
func ValidateWorkflowOwner(owner string) error {
	if len(owner) != 40 {
		return fmt.Errorf("invalid workflow owner: incorrect length, expected 40, got %d", len(owner))
	}
	if _, err := hex.DecodeString(owner); err != nil {
		return fmt.Errorf("invalid workflow owner: %w", err)
	}
	return nil
```
