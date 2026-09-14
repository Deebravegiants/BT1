Based on my investigation, I found a concrete, reachable analog: a **negative-length panic** (`strings.Repeat` with a negative count) triggered by unauthenticated crafted input to the workflow-execution HTTP trigger handler, reachable *before* any authentication/JWT check is performed.

### Title
Unauthenticated DoS via `strings.Repeat` negative-count panic in `normalizeHex` - (File: `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`)

### Summary
The external report describes an integer overflow/wraparound in NATS Server that a remote, unauthenticated attacker can exploit by sending a crafted request to crash the server. The closest reachable analog in this codebase is an arithmetic-underflow bug in the Gateway's HTTP-trigger workflow ID normalization: a crafted `workflowID` causes a negative argument to `strings.Repeat`, which panics in Go, and this code path executes **before** JWT authorization is checked.

### Finding Description
`validateHexInput` only checks that the field is lowercase, `len(input) <= expectedLength`, and that the string (after optionally trimming a `0x` prefix) is valid hex: [1](#0-0) 

It does not require the `0x` prefix to actually be present. `workflowIDLength` is defined as 66 (i.e., `"0x"` + 64 hex chars): [2](#0-1) 

If a caller submits a `workflowID` of exactly 66 lowercase hex characters **without** the `0x` prefix, `validateHexInput` passes: `len(input) == expectedLength` (not `>`), and `hex.DecodeString` succeeds on an even-length (66) hex string.

Later, `resolveWorkflowID` calls `normalizeHex(workflowID, workflowIDLength)`: [3](#0-2) 

Here, `hexStr := strings.TrimPrefix(input, "0x")` leaves the 66-character string unchanged (no `0x` to strip), so `len(hexStr) == 66`. `expectedHexLength := length - 2 == 64`. The computed repeat count is `expectedHexLength - len(hexStr) == 64 - 66 == -2`. `strings.Repeat` panics on a negative count, causing an unrecovered panic during request handling.

Critically, this path is reached before authentication: `HandleUserTriggerRequest` calls `resolveWorkflowID` (which triggers the panic) *before* `authorizeRequest` (JWT verification): [4](#0-3) 

The README documents that "All trigger requests must include valid JWT tokens," implying the JWT check is expected to gate all processing, but in the actual code the vulnerable hex-normalization logic runs beforehand.

### Impact Explanation
An unauthenticated, unprivileged client sending a single crafted JSON-RPC `workflows.execute` request to the Gateway's user-facing HTTP endpoint can trigger a Go panic inside the request-handling goroutine. Depending on how the outer HTTP server handles panics (recover middleware vs. bare `net/http`), this can terminate the connection or, if unrecovered, crash the Gateway process — a remote unauthenticated denial-of-service, matching the crash impact described in the reference advisory (CVSS `A:H`). I was not able to confirm within the available tool budget whether a panic-recovery middleware wraps `gateway.ProcessRequest` / the user-facing HTTP server (`core/services/gateway/network`), so the blast radius (single request failure vs. full process crash) is not fully verified.

### Likelihood Explanation
High. No authentication, no signature, and no special network position is required — only a JSON payload with a 66-character `workflowID` value lacking the `0x` prefix, composed of valid lowercase hex characters. This is trivial to construct and send to the Gateway's public HTTP-facing endpoint that accepts `workflows.execute` trigger requests.

### Recommendation
- In `validateHexInput`, require the `0x` prefix explicitly (e.g., `strings.HasPrefix(input, "0x")`) rather than only checking overall length, and reject inputs that don't start with `0x`.
- In `normalizeHex`, guard against `expectedHexLength - len(hexStr)` being negative and return an error instead of calling `strings.Repeat` with an unchecked/possibly negative value.
- Move JWT/authorization checks (`authorizeRequest`) ahead of any input-transforming logic (`resolveWorkflowID`/`normalizeHex`) so malformed or malicious payloads are rejected before further processing.
- Add a panic-recovery wrapper around per-request Gateway handling to prevent any single crafted request from destabilizing the whole process, as defense-in-depth.

### Proof of Concept
Send a `workflows.execute` JSON-RPC request to the Gateway's user HTTP endpoint with a `workflowID` of exactly 66 lowercase hex characters, omitting the `0x` prefix, e.g.:
```json
{
  "jsonrpc": "2.0",
  "id": "poc-1",
  "method": "workflows.execute",
  "params": {
    "input": {},
    "workflow": {
      "workflowID": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    }
  }
}
```
(66 `a` characters, no `0x` prefix.) This passes `validateHexInput` (length equals `workflowIDLength`=66, lowercase, valid hex when decoded without a prefix), then reaches `normalizeHex(workflowID, 66)` in `resolveWorkflowID`, where `strings.Repeat("0", 64-66)` panics — before any JWT/authorization check occurs. [5](#0-4)

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-109)
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
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L267-283)
```go
func validateHexInput(input string, expectedLength int) error {
	if input != strings.ToLower(input) {
		return errors.New("must be lowercase")
	}

	if len(input) > expectedLength {
		return fmt.Errorf("hex string too long: expected at most %d characters, got %d", expectedLength, len(input))
	}

	hexStr := strings.TrimPrefix(input, "0x")
	_, err := hex.DecodeString(hexStr)
	if err != nil {
		return errors.New("must be a valid hex string")
	}

	return nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L333-340)
```go
// normalizeHex normalizes a hex string by stripping 0x prefix, padding with leading zeros, and adding 0x prefix back
func normalizeHex(input string, length int) string {
	hexStr := strings.TrimPrefix(input, "0x")
	// length-2 because we'll add "0x" prefix
	expectedHexLength := length - 2
	paddedHex := strings.Repeat("0", expectedHexLength-len(hexStr)) + hexStr
	return "0x" + paddedHex
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L342-353)
```go
func (h *httpTriggerHandler) resolveWorkflowID(ctx context.Context, triggerReq *jsonrpc.Request[gateway_common.HTTPTriggerRequest], requestID string, callback handlers.Callback) (string, error) {
	h.lggr.Debugw("resolving workflow ID", "workflowID", triggerReq.Params.Workflow.WorkflowID, "workflowOwner", triggerReq.Params.Workflow.WorkflowOwner, "workflowName", triggerReq.Params.Workflow.WorkflowName, "workflowTag", triggerReq.Params.Workflow.WorkflowTag, "requestID", requestID)
	workflowID := triggerReq.Params.Workflow.WorkflowID
	if workflowID != "" {
		workflowID = normalizeHex(workflowID, workflowIDLength)
		_, found := h.workflowMetadataHandler.GetWorkflowReference(workflowID)
		if !found {
			h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, fmt.Sprintf("Workflow not found. 'workflowID' %s is not a valid workflow ID", workflowID), callback)
			return "", errors.New("workflow not found")
		}
		return workflowID, nil
	}
```
