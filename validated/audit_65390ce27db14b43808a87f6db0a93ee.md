Confirmed: the auth error propagates all the way to the unprivileged HTTP/gateway client. In `core/services/gateway/handlers/vault/handler.go` line 433, `ProcessRequest`'s error (which wraps `AuthorizeRequest`'s error, including the digest-mismatch message from `jwt_based_auth.go`) is sent verbatim as `"request not authorized: " + err.Error()` back to the caller, and this exact pattern is asserted in tests (`gw_handler_test.go` lines 436-438, 519-520) showing the raw underlying error text reaches the JSON-RPC error response delivered to the gateway's HTTP client.

### Title
JWT auth handler leaks the expected (server-computed) request digest to unauthenticated callers, enabling request/token forgery — (File: `core/capabilities/vault/jwt_based_auth.go`)

### Summary
`jwtBasedAuth.AuthorizeRequest` computes the expected request digest server-side and, when it doesn't match the digest claimed inside the caller-supplied JWT, returns an error string that embeds both values verbatim: `fmt.Errorf("request digest mismatch: computed=%s claimed=%s", requestDigest, claims.RequestDigest)` [1](#0-0) . This is structurally the same bug class as GHSA-qpvx-gpqm-g98j/CVE-2019-7644: the server discloses the value it independently computed and expects to see in a signed/claimed field, inside an error message shown to the requester who is trying to forge that value.

### Finding Description
`validateToken` verifies the JWT's cryptographic signature via JWKS first [2](#0-1) . Only after signature verification succeeds does `AuthorizeRequest` independently compute `requestDigest` from the request body and compare it against the `RequestDigest` claim carried (and presumably bound) inside the already-signed JWT payload [3](#0-2) . Because the mismatch error interpolates the server's own freshly computed digest into the response text, any caller who can get a validly-signed JWT for themselves but wants to bind it to a different or replayed request body can simply read `computed=%s` from the error and re-issue a request whose digest matches — this is effectively a "leak the expected value" oracle analogous to the Auth0 advisory's JWT signature leak, just with the digest binding rather than the signature bytes.

`AuthorizeRequest`'s error return is wrapped only lightly as it moves up the call stack — `authorizer.AuthorizeRequest` passes it through unchanged [4](#0-3) , `authorizeAndStamp` wraps it as `"request not authorized: %w"` [5](#0-4) , and the gateway handler forwards `"request not authorized: " + err.Error()` straight into the JSON-RPC error response sent back to the HTTP caller [6](#0-5) . Tests explicitly assert this exact concatenated error text reaches the outbound gateway response payload [7](#0-6) , confirming there is no redaction layer between this internal error and the unprivileged network client.

### Impact Explanation
An unprivileged actor who can obtain any validly-signed Auth0 JWT for the vault capability (e.g. a legitimate low-privilege org token, or one with a stale/mismatched digest) can use the disclosed `computed=` digest to iteratively discover what request body/binding value the server expects, undermining the request-digest binding that is supposed to tie a specific JWT-authorized call to a specific request payload. This weakens (though does not fully break, since the JWT signature itself is still required) the intended cryptographic binding between the caller's signed token and the exact vault operation being authorized, and could facilitate request retargeting/replay against the vault secrets API (create/update/delete/list secrets) if combined with any other digest-computation or claim-reuse weakness.

### Likelihood Explanation
Reaching this code path requires only an HTTP/JSON-RPC request to the gateway's vault endpoint carrying `req.Auth` set (any syntactically valid, signature-valid JWT with a `request_digest` claim not matching the current request body) — no special privilege, network position, or node compromise is needed, satisfying the "unprivileged client request" and "internet-facing gateway" scope. The error text is deterministic and always returned on every digest mismatch, so the leak is trivially and repeatably observable.

### Recommendation
Do not interpolate the server-computed digest (or any other server-side expected/secret value) into user-facing error messages. Return a generic `ErrInvalidToken`-style error (as is already done for other JWT validation failures such as missing kid, bad issuer, etc.) and log the `computed`/`claimed` values only at `Debugw`/internal logger level, consistent with how other sensitive comparisons in this file are already logged rather than returned to the caller.

### Proof of Concept
1. Obtain any validly Auth0-signed JWT satisfying `iss`, `aud`, `exp`, `org_id`, tenant, and `claim_vault_secret_management_enabled`, but with a `request_digest` claim that does not match the request body being sent.
2. Send a `secrets/create` (or list/update/delete) JSON-RPC request to the gateway's vault endpoint with `Auth` set to this token.
3. `jwtBasedAuth.AuthorizeRequest` signature/claims checks pass, but the digest comparison at `core/capabilities/vault/jwt_based_auth.go:214-217` fails and returns `request digest mismatch: computed=<X> claimed=<Y>`.
4. This error propagates unmodified through `authorizeAndStamp` and `handler.HandleJSONRPCUserMessage` into the JSON-RPC `error.message` field of the HTTP response returned to the caller, revealing the server-computed digest `<X>` that the attacker did not otherwise know.

### Citations

**File:** core/capabilities/vault/jwt_based_auth.go (L208-217)
```go
	requestDigest, err := req.Digest()
	if err != nil {
		v.lggr.Debugw("JWTBasedAuth failed to compute request digest", "method", req.Method, "requestID", req.ID, "orgID", claims.OrgID, "workflowOwner", claims.WorkflowOwner, "error", err)
		return nil, fmt.Errorf("failed to compute request digest: %w", err)
	}

	if !strings.EqualFold(requestDigest, claims.RequestDigest) {
		v.lggr.Debugw("JWTBasedAuth request digest mismatch", "method", req.Method, "requestID", req.ID, "orgID", claims.OrgID, "workflowOwner", claims.WorkflowOwner, "computedDigest", requestDigest, "claimedDigest", claims.RequestDigest)
		return nil, fmt.Errorf("request digest mismatch: computed=%s claimed=%s", requestDigest, claims.RequestDigest)
	}
```

**File:** core/capabilities/vault/jwt_based_auth.go (L258-277)
```go
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (any, error) {
		if _, methodOK := token.Method.(*jwt.SigningMethodRSA); !methodOK {
			return nil, fmt.Errorf("%w: unsupported alg %v", ErrInvalidToken, token.Header["alg"])
		}
		return rsaKey, nil
	},
		jwt.WithIssuer(v.issuerURL),
		jwt.WithAudience(v.audience),
		jwt.WithExpirationRequired(),
		jwt.WithIssuedAt(),
		jwt.WithLeeway(jwtValidationLeeway),
	)
	if err != nil {
		return nil, fmt.Errorf("%w: %w. Expected Issuer: %s, Actual Issuer: %s", ErrInvalidToken, err, v.issuerURL, unverified.Claims.(jwt.MapClaims)["iss"])
	}

	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok || !token.Valid {
		return nil, ErrInvalidToken
	}
```

**File:** core/capabilities/vault/authorizer.go (L99-103)
```go
func (a *authorizer) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	authResult, err := a.authorizeRequest(ctx, req)
	if err != nil {
		return nil, err
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L271-276)
```go
	authResult, err := p.authorizer.AuthorizeRequest(ctx, *req)
	if err != nil {
		authErr := fmt.Errorf("request not authorized: %w", err)
		p.lggr.Errorw("gateway vault request authorization failed", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "incomingOwner", incomingOwner, "error", authErr)
		return nil, authErr
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L428-434)
```go
	if err != nil {
		if vaultcap.IsInvalidVaultParamsError(err) {
			return h.sendImmediateUserResponse(ctx, req, callback, api.InvalidParamsError, err)
		}
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
		return errors.New("request not authorized: " + err.Error())
	}
```

**File:** core/capabilities/vault/gw_handler_test.go (L434-439)
```go
				ra.EXPECT().AuthorizeRequest(mock.Anything, mock.Anything).Return(nil, errors.New("not allowlisted"))
				gc.On("SendToGateway", mock.Anything, "gateway-1", mock.MatchedBy(func(resp *jsonrpc.Response[json.RawMessage]) bool {
					return resp.Error != nil &&
						resp.Error.Code == api.ToJSONRPCErrorCode(api.HandlerError) &&
						resp.Error.Message == "request not authorized: not allowlisted"
				})).Return(nil)
```
