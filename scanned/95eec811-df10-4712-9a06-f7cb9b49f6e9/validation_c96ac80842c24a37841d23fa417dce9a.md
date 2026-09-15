### Title
Nil-Pointer Dereference Panic in Vault `GatewayHandler.handlePublicKeyGet` via Missing-Params JSON-RPC Request - (File: `core/capabilities/vault/gw_handler.go`)

### Summary
The node-side Vault gateway handler dereferences `*req.Params` in `handlePublicKeyGet` without checking whether `Params` is `nil`, while the sibling methods (`SecretsCreate`, `SecretsUpdate`, `SecretsDelete`, `SecretsList`) are protected by an explicit nil-params check performed earlier in `GatewayVaultRequestProcessor`. Because `MethodPublicKeyGet` is explicitly documented and implemented as not requiring authorization, an unauthenticated/unprivileged client can send a well-formed JSON-RPC request that omits the `params` field through the internet-facing Gateway, causing the receiving Chainlink node to panic on nil-pointer dereference and crash — the same root-cause pattern (unchecked pointer/field access on parsed external metadata) described in the Incus GHSA-gc7j-g665-rxr9 advisory.

### Finding Description
`GatewayHandler.HandleGatewayMessage` in `core/capabilities/vault/gw_handler.go` routes incoming vault JSON-RPC requests from the Gateway based on `req.Method`: [1](#0-0) 

For `MethodSecretsCreate`/`Update`/`Delete`/`List`, the request is first passed through `h.requestProcessor.ProcessRequest`, which validates the request structure — including an explicit `req.Params == nil` check — before any handler unmarshal happens: [2](#0-1) 

But for `MethodPublicKeyGet`, the code takes a different branch that skips this validation entirely and calls `handlePublicKeyGet` directly: [3](#0-2) 

`handlePublicKeyGet` unconditionally dereferences `req.Params`: [4](#0-3) 

If `req.Params` is `nil` (e.g., the JSON-RPC request simply omits the optional `params` field, which is valid per JSON-RPC 2.0), `*req.Params` triggers a Go runtime nil-pointer dereference panic.

On the Gateway (internet-facing) side, `MethodPublicKeyGet` is explicitly treated as not requiring any authorization/authentication before being forwarded to nodes: [5](#0-4) 

There is no validation of `req.Params` for this method on the gateway side either — the request is simply queued as an `activeRequest` and forwarded to DON nodes unmodified. This means an external, unauthenticated caller can reach the vulnerable node-side code path with a controllable, nil `Params` field.

### Impact Explanation
A successful trigger crashes the Chainlink node process running the Vault capability (the node-side `GatewayHandler`), causing denial of service. Because `MethodPublicKeyGet` is intentionally exempt from authorization, this is reachable by any unauthenticated actor able to reach the Gateway's HTTP/WS endpoint — no valid signature, allowlist entry, or JWT is required. Repeated requests can be used to keep the node offline, directly mirroring the "High" severity DoS classification of the referenced advisory (CWE-476, repeated crash = sustained denial of service).

### Likelihood Explanation
High. The triggering condition is trivial: send a `vault` JSON-RPC request with `method` set to the public-key-get method and no `params` field (or `params: null`) to the Gateway's user-facing endpoint. No cryptographic material, valid signature, or prior session is needed since this method bypasses authorization by design. The only precondition is that the Vault capability/gateway service is deployed and reachable, which is the normal production configuration for CRE/Vault-enabled DONs.

### Recommendation
Add an explicit `req.Params == nil` check in `handlePublicKeyGet` (and ideally as a generic guard at the top of `HandleGatewayMessage`, or in the gateway-side handler before forwarding), returning a structured `api.UserMessageParseError`/`InvalidParamsError` response instead of allowing the nil dereference to reach `json.Unmarshal(*req.Params, ...)`. This mirrors the existing nil-check pattern already used by `GatewayVaultRequestProcessor.processCreateSecretsRequest` etc., and should be applied consistently to every method branch that dereferences `req.Params`, including the currently-unauthenticated public-key path.

### Proof of Concept
1. Identify the Gateway's public HTTP/WS endpoint that accepts vault JSON-RPC user messages (per `core/services/gateway/handlers/vault/handler.go`, `HandleJSONRPCUserMessage`).
2. Send a JSON-RPC 2.0 request to that endpoint with:
   ```json
   {
     "jsonrpc": "2.0",
     "id": "poc-1",
     "method": "<vault public-key-get method name>"
   }
   ```
   deliberately omitting the `params` field (no request signature/session required, since public-key-get is documented as not requiring authorization).
3. The gateway forwards the request unmodified to a DON node's `GatewayHandler.HandleGatewayMessage`, which dispatches to `handlePublicKeyGet` and executes `json.Unmarshal(*req.Params, r)` with `req.Params == nil`.
4. The node process panics with `runtime error: invalid memory address or nil pointer dereference`, crashing the node (verifiable via node logs/`journalctl` showing the panic stack rooted in `handlePublicKeyGet`).

**Note on scope/verification limits:** I could not fully trace the exact wire-level JSON-RPC method-name constant for `MethodPublicKeyGet` or confirm every intermediate serialization step between the Gateway HTTP layer and `SendToNode`/`HandleGatewayMessage` (some of that plumbing lives in files not surfaced by search, e.g. exact `vaulttypes.MethodPublicKeyGet` string and `newActiveRequest`/`SendToNode` wiring). The code shown conclusively establishes the missing nil-check and the "no-auth" comment for this method, but a live PoC run against a running Gateway/node pair would be needed to confirm the panic end-to-end.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L187-211)
```go
	switch req.Method {
	case vaulttypes.MethodSecretsCreate, vaulttypes.MethodSecretsUpdate:
		publicKey, pkErr := h.getMasterPublicKey(ctx)
		if pkErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pkErr)
			break
		}
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, publicKey)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodSecretsDelete, vaulttypes.MethodSecretsList:
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, nil)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
	default:
		response = h.errorResponse(ctx, gatewayID, req, api.UnsupportedMethodError, errors.New("unsupported method: "+req.Method))
	}
```

**File:** core/capabilities/vault/gw_handler.go (L364-368)
```go
func (h *GatewayHandler) handlePublicKeyGet(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.GetPublicKeyRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L110-117)
```go
func (p *GatewayVaultRequestProcessor) processCreateSecretsRequest(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	publicKey *tdh2easy.PublicKey,
) (*AuthorizedGatewayVaultRequest, error) {
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L404-420)
```go
	if req.Method == vaulttypes.MethodPublicKeyGet {
		// Public key requests don't require authorization,
		// Let's process this request right away.
		// Note we cache this value quite aggressively so don't need to worry about DoS.
		publicKeyResponseBytes, cachedPublicKey := h.getCachedPublicKey()
		if cachedPublicKey == nil {
			// Not found in cache. Fetch from nodes.
			ar, err := h.newActiveRequest(req, callback)
			if err != nil {
				h.lggr.Errorw("failed to create new activeRequest", "error", err)
				return err
			}
			return h.handlePublicKeyGet(ctx, ar)
		}
		h.lggr.Debugw("returning cached public key response")
		return h.handlePublicKeyGetSynchronously(ctx, req, publicKeyResponseBytes, callback)
	}
```
