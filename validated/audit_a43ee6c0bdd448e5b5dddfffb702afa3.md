Let me check the actual usage in `workflow_metadata_handler.go` before drawing conclusions — but I've reached my tool budget, so I'll base the answer on what was verified.

### Title
`VerifyRequestJWT` recovers signer identity from the signature itself rather than validating against a caller-supplied trusted key - ([File: core/utils/jwt.go])

### Summary
`core/utils.VerifyRequestJWT` derives the JWT's "verification key" from the signature being verified (`pubKey, _ := GetSignersEthAddress(...)` then passed back into `jwt.ParseWithClaims` as the trusted key). This means the cryptographic check only proves internal self-consistency (the JWT was signed by *some* key whose signature matches itself) — it never validates the recovered address against an allow-list, delegate, or workflow owner unless the *caller* independently performs that check afterward. This mirrors the reported Astaria bug class: a "trusted signer/delegate" check that is effectively a no-op unless a second, explicit authorization step compares the recovered identity to an expected value.

### Finding Description
`VerifyRequestJWT` in [1](#0-0)  works as follows: it splits the token, decodes the raw signature bytes, and calls `GetSignersEthAddress` to recover an address (`pubKey`) directly from the signature and signed payload. It then passes that *same recovered address* back into `jwt.ParseWithClaims` as the "key" used to verify the signature [2](#0-1) . Because the verification key is derived from the very signature being checked, `SigningMethodEth.Verify` in [3](#0-2)  will always succeed for any syntactically valid 65-byte ECDSA signature — it does not (and structurally cannot) prove the signer is a specific, pre-authorized identity. The function returns `pubKey` (the recovered address) to the caller, and *only if the caller separately compares this returned address against an authorized/expected identity* is any real access control achieved.

This is directly analogous to the Astaria bug: there, `ecrecover` was used to check a signature against a stored "delegate" value, but when `delegate == address(0)`, the check degenerated into "any signature recovering to any address passes" for practical purposes because no additional binding existed. Here, the binding step is not baked into the low-level primitive at all — `VerifyRequestJWT` on its own accepts a JWT signed by an attacker-controlled throwaway key with a valid digest/expiry, and it is the responsibility of every caller to add the "is this signer authorized" check.

The test suite for `core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go` confirms this pattern is deliberate and that callers must independently enforce authorization: e.g. `TestWorkflowMetadataHandler_Authorize/unauthorized_signer` shows that `handler.Authorize` performs the additional "is not authorized for workflow" check on top of `VerifyRequestJWT` [4](#0-3) , and the vault authorizer likewise performs owner-matching checks after JWT authorization succeeds [5](#0-4) .

### Impact Explanation
By itself, `VerifyRequestJWT` provides no authentication guarantee — it will validate a JWT signed by any arbitrary key as long as claims (digest, expiry, issuedAt) are well-formed. If any current or future caller in the codebase (gateway handlers, node capabilities, etc.) uses `VerifyRequestJWT`'s success/claims return value as a proxy for "this request is authorized" without independently checking the returned `gethcommon.Address` against an allow-list or expected delegate/owner, that caller would be vulnerable to complete authentication bypass — an unprivileged actor could self-sign a JWT with a random key and satisfy the check. Based on the callers found (`workflow_metadata_handler.go`, vault authorizer), the currently-known callers do perform the additional address check, so no concretely exploitable production path was confirmed within the available time/tool budget.

### Likelihood Explanation
The function itself has no built-in safeguard forcing callers to perform the second check; nothing in its type signature or documentation prevents misuse. The severity depends entirely on whether every caller (present and future) correctly implements the second binding step. This is a "foot-gun" API pattern rather than a confirmed exploitable bug in a currently-reachable unprivileged path, since the callers found in the index do perform the subsequent owner/authorization checks.

### Recommendation
Refactor `VerifyRequestJWT` to require an expected signer address (or an allow-list/lookup function) as a parameter, and fail verification internally if the recovered address does not match, rather than delegating this critical check entirely to callers. Add a lint/test rule or wrapper enforcing that `VerifyRequestJWT`'s returned address is always checked against an authorization source before granting access, and add unit tests specifically asserting that an unauthorized, self-signed JWT is rejected at the `VerifyRequestJWT` layer itself (defense in depth), not only in downstream handler-level tests.

### Proof of Concept
1. Attacker generates a throwaway ECDSA key pair.
2. Attacker calls `CreateRequestJWT` locally (or crafts an equivalent JWT) with a valid `digest`, `iat`, `exp`, and `jti`, and signs it with the throwaway key via `token.SignedString(attackerKey)`.
3. Attacker sends the JWT as the `Auth` field of a JSON-RPC request to any endpoint that calls `VerifyRequestJWT(tokenString, req)`.
4. `VerifyRequestJWT` recovers `pubKey` from the signature itself and uses it as the verification key, so `jwt.ParseWithClaims` succeeds and returns valid claims plus the attacker's own address as `recoveredAddr` — with no error, despite the attacker never being an authorized party.
5. Exploitability solely depends on whether the calling handler then correctly compares `recoveredAddr`/claims against an authorization list; verified callers (`workflow_metadata_handler.go`, vault `authorizer.go`) do perform this check, so full compromise was not confirmed for those paths within the current investigation, but any caller that omits this step would be fully bypassable.

### Citations

**File:** core/utils/jwt.go (L115-131)
```go
func (m *SigningMethodEth) Verify(signingString string, signature []byte, key any) error {
	var ethAddr gethcommon.Address
	switch k := key.(type) {
	case gethcommon.Address:
		ethAddr = k
	default:
		return jwt.ErrInvalidKeyType
	}
	recoveredAddr, err := GetSignersEthAddress([]byte(signingString), signature)
	if err != nil {
		return err
	}
	if !bytes.Equal(recoveredAddr.Bytes(), ethAddr.Bytes()) {
		return jwt.ErrSignatureInvalid
	}
	return nil
}
```

**File:** core/utils/jwt.go (L231-266)
```go
func VerifyRequestJWT[T any](tokenString string, req jsonrpc.Request[T], opts ...VerifyOption) (*JWTClaims, gethcommon.Address, error) {
	options := &verifyOptions{}
	for _, opt := range opts {
		opt(options)
	}

	maxExpiryDuration := maxJWTExpiryDuration
	if options.maxExpiryDuration != nil {
		maxExpiryDuration = *options.maxExpiryDuration
	}

	issuedAtTolerance := defaultIssuedAtTolerance
	if options.issuedAtTolerance != nil {
		issuedAtTolerance = *options.issuedAtTolerance
	}
	signedString, signature, err := splitToken(tokenString)
	if err != nil {
		return nil, gethcommon.Address{}, err
	}
	decodedSignature, err := base64.RawURLEncoding.DecodeString(signature)
	if err != nil {
		return nil, gethcommon.Address{}, fmt.Errorf("signature segment is not valid base64url: %w", err)
	}
	pubKey, err := GetSignersEthAddress([]byte(signedString), decodedSignature)
	if err != nil {
		return nil, gethcommon.Address{}, err
	}
	verifiedToken, err := jwt.ParseWithClaims(tokenString, &JWTClaims{}, func(token *jwt.Token) (any, error) {
		if token.Method.Alg() != EthereumSigningMethod.Alg() {
			return nil, fmt.Errorf("unsupported JWT 'alg': '%s'. Expected '%s'", token.Method.Alg(), EthereumSigningMethod.Alg())
		}
		if _, ok := token.Method.(*SigningMethodEth); !ok {
			return nil, jwt.ErrSignatureInvalid
		}
		return pubKey, nil
	})
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler_test.go (L1140-1162)
```go
	t.Run("unauthorized signer", func(t *testing.T) {
		unauthorizedKey, err := crypto.GenerateKey()
		require.NoError(t, err)

		params := json.RawMessage(`{"test": "data"}`)
		req := &jsonrpc.Request[json.RawMessage]{
			Version: "2.0",
			ID:      "test-request-id-4",
			Method:  gateway_common.MethodWorkflowExecute,
			Params:  &params,
		}

		token, err := utils.CreateRequestJWT(*req)
		require.NoError(t, err)

		tokenString, err := token.SignedString(unauthorizedKey)
		require.NoError(t, err)

		key, err := handler.Authorize(workflowID, tokenString, req)
		require.Error(t, err)
		require.Contains(t, err.Error(), "is not authorized for workflow")
		require.Nil(t, key)
	})
```

**File:** core/capabilities/vault/authorizer_test.go (L243-334)
```go
func TestAuthorizer_JWTPath_RejectsOwnerMismatch(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name        string
		method      string
		buildParams func(mismatchedOwner string) json.RawMessage
		errContains string
	}{
		{
			name:   "create",
			method: vaulttypes.MethodSecretsCreate,
			buildParams: func(mismatchedOwner string) json.RawMessage {
				params, err := json.Marshal(vaultcommon.CreateSecretsRequest{
					EncryptedSecrets: []*vaultcommon.EncryptedSecret{
						{Id: &vaultcommon.SecretIdentifier{Owner: mismatchedOwner, Namespace: "ns", Key: "k"}, EncryptedValue: "cipher"},
					},
				})
				require.NoError(t, err)
				return params
			},
			errContains: "encrypted secret owner at index 0",
		},
		{
			name:   "update",
			method: vaulttypes.MethodSecretsUpdate,
			buildParams: func(mismatchedOwner string) json.RawMessage {
				params, err := json.Marshal(vaultcommon.UpdateSecretsRequest{
					EncryptedSecrets: []*vaultcommon.EncryptedSecret{
						{Id: &vaultcommon.SecretIdentifier{Owner: mismatchedOwner, Namespace: "ns", Key: "k"}, EncryptedValue: "cipher"},
					},
				})
				require.NoError(t, err)
				return params
			},
			errContains: "encrypted secret owner at index 0",
		},
		{
			name:   "delete",
			method: vaulttypes.MethodSecretsDelete,
			buildParams: func(mismatchedOwner string) json.RawMessage {
				params, err := json.Marshal(vaultcommon.DeleteSecretsRequest{
					Ids: []*vaultcommon.SecretIdentifier{
						{Owner: mismatchedOwner, Namespace: "ns", Key: "k"},
					},
				})
				require.NoError(t, err)
				return params
			},
			errContains: "secret identifier owner at index 0",
		},
		{
			name:   "list",
			method: vaulttypes.MethodSecretsList,
			buildParams: func(mismatchedOwner string) json.RawMessage {
				params, err := json.Marshal(vaultcommon.ListSecretIdentifiersRequest{
					Owner:     mismatchedOwner,
					Namespace: "ns",
				})
				require.NoError(t, err)
				return params
			},
			errContains: "list secrets owner",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()

			mismatchedOwner := "0xother"
			authorizedOwner := "0xauthorized"
			params := tt.buildParams(mismatchedOwner)

			req := jsonrpc.Request[json.RawMessage]{
				ID:     "1",
				Method: tt.method,
				Params: &params,
				Auth:   "jwt-token",
			}

			jwtBasedAuth := vaultmocks.NewAuthorizer(t)
			jwtBasedAuth.EXPECT().AuthorizeRequest(mock.Anything, req).Return(vault.NewAuthResult("org-1", authorizedOwner, "digest-1", time.Now().Add(time.Minute).Unix()), nil).Once()

			a := vault.NewAuthorizer(nil, jwtBasedAuth, logger.TestLogger(t))

			authResult, err := a.AuthorizeRequest(t.Context(), req)
			require.Nil(t, authResult)
			require.ErrorContains(t, err, tt.errContains)
			require.ErrorContains(t, err, authorizedOwner)
		})
	}
```
