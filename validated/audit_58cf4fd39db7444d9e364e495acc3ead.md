### Title
Vault gateway `handleSecretsDelete` does not enforce the authorized owner on delete requests, allowing an authorized caller to delete another owner's secrets - ([File: core/capabilities/vault/gw_handler.go])

### Summary
The Vault gateway node handler authorizes `MethodSecretsDelete` requests through the same generic `AuthorizeRequest` pipeline as `MethodSecretsList`, but only `handleSecretsList` re-stamps the request with the caller's authorized owner before executing the operation. `handleSecretsDelete` unmarshals the client-supplied `DeleteSecretsRequest` and forwards it directly to `secretsService.DeleteSecrets` without binding the `Owner` field(s) inside the request to the identity returned by `AuthResult`.

### Finding Description
In `core/capabilities/vault/gw_handler.go`, `HandleGatewayMessage` runs both `MethodSecretsDelete` and `MethodSecretsList` through `h.requestProcessor.ProcessRequest(ctx, req, nil)`, producing an `authResult` that carries the authorized owner identity [1](#0-0) .

For list requests, the handler explicitly overwrites the client-controlled `Owner` field with the authorized owner before calling the secrets service, preventing a caller from reading another owner's secret identifiers: [2](#0-1) 

For delete requests, no equivalent owner stamping/enforcement happens — the unmarshaled `DeleteSecretsRequest` (whose `Ids[].Owner` fields are attacker-controlled JSON input) is passed straight to `secretsService.DeleteSecrets`: [3](#0-2) 

This is the same class of bug as the reported ERC20 issue: a caller who is authenticated/authorized for their own scope (analogous to the "minter" role) can supply an `Owner` value belonging to a different party and trigger destructive action (secret deletion) against that other party's data, instead of the action being scoped to the caller's own identity as derived from authentication. The `AuthorizeRequest`/`AllowListBasedAuth` layer (`core/capabilities/vault/allow_list_based_auth.go`) authorizes based on a digest of the *entire* request content for allowlist-based auth, which may coincidentally bind the owner for that specific auth mode, but the JWT-based (`Auth0`) authorization path returns an owner identity independent of request content (as seen in `authResult("org-1", "0xworkflow")`-style results used across tests), and the handler code makes no attempt to cross-check that identity against the `Owner` values embedded in the delete request the same way it does for list.

### Impact Explanation
If `secretsService.DeleteSecrets` does not itself perform an independent ownership check against the caller's authenticated identity (that implementation was not visible in the indexed code), an authorized-but-unprivileged workflow owner could delete secrets belonging to any other owner by crafting a `DeleteSecretsRequest` with a different `Owner` in the identifiers. This is a direct cross-user destructive-action / unauthorized-data-deletion analog to "minter can burn anyone's tokens" — loss of another user's secret data and denial of their ability to use their own vault entries.

### Likelihood Explanation
Likelihood depends on whether `secretsService.DeleteSecrets` (implementation not indexed/available) re-validates ownership internally. Given that the handler layer explicitly performs this stamping for `List` but conspicuously omits it for `Delete`, this looks like an inconsistency/oversight rather than an intentional design, making it a plausible reachable path if the downstream service trusts the `Owner` field from the wire request.

### Recommendation
Mirror the `handleSecretsList` pattern in `handleSecretsDelete`: after authorization, override or validate every `Ids[].Owner` in the `DeleteSecretsRequest` against `authResult.AuthorizedOwner()` (or reject the request if any identifier's owner does not match), rather than trusting client-supplied owner values, ensuring deletion is always scoped to the authenticated caller's own secrets.

### Proof of Concept
1. Caller A obtains a valid `AuthResult` for owner `A` (e.g., via allowlist or JWT auth) for `MethodSecretsDelete`.
2. Caller A crafts `DeleteSecretsRequest.Ids = [{Owner: "B", Key: "...", Namespace: "..."}]`.
3. `HandleGatewayMessage` authorizes the request via `ProcessRequest` (owner `A` authorized) and then calls `handleSecretsDelete`, which unmarshal-and-forwards the request unmodified: [3](#0-2) 
4. Unless `secretsService.DeleteSecrets` independently re-checks ownership, owner `B`'s secrets are deleted by caller `A`.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L200-206)
```go
	case vaulttypes.MethodSecretsDelete, vaulttypes.MethodSecretsList:
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, nil)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
```

**File:** core/capabilities/vault/gw_handler.go (L313-323)
```go
func (h *GatewayHandler) handleSecretsDelete(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.DeleteSecretsRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

	h.lggr.Debugw("Processing authorized delete secrets request", "request", r.String())
	resp, err := h.secretsService.DeleteSecrets(ctx, r)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.HandlerError, fmt.Errorf("failed to delete secrets: %w", err))
	}
```

**File:** core/capabilities/vault/gw_handler.go (L338-346)
```go
func (h *GatewayHandler) handleSecretsList(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage], authResult *AuthResult) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.ListSecretIdentifiersRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}
	r.Owner = authResult.AuthorizedOwner()

	h.lggr.Debugw("Processing authorized list secrets request", "request", r.String())
	resp, err := h.secretsService.ListSecretIdentifiers(ctx, r)
```
