## Finding [1](#0-0) 

### Title
Ethereum-signed request JWT verification never validates `iss`/`aud` (domain-separation) claims, enabling cross-target signature replay - (File: core/utils/jwt.go)

### Summary
The Teller finding is a missing domain-separator (`chainID`) in an EIP-191 signature, letting a lender's attestation signature valid on one chain be replayed on another. The closest reachable analog in this repo is `utils.VerifyRequestJWT`/`utils.CreateRequestJWT`, which implement an Ethereum-signature-based JWT scheme used to authorize unprivileged HTTP-trigger workflow requests through the gateway. The claims struct carries `Issuer`/`Audience`/`Subject` fields (populated by `CreateRequestJWT`), but `VerifyRequestJWT` never checks them — it validates only signature, `exp`, `iat`, `jti` (via caller-side replay cache) and the `digest` claim.

### Finding Description
`CreateRequestJWT` builds a JWT with an ECDSA/secp256k1 ("ETH") signature over `header.payload`, embedding `Digest` (hash of only the JSON-RPC request's method+params), plus optional `Issuer`/`Audience`/`Subject`: [2](#0-1) 

`VerifyRequestJWT` recovers the signer address from the raw signature bytes and calls `jwt.ParseWithClaims` with **no** `jwt.WithIssuer(...)` or `jwt.WithAudience(...)` options, unlike the sibling Vault OAuth path (`jwt_based_auth.go`) which explicitly enforces `jwt.WithIssuer(v.issuerURL)` and `jwt.WithAudience(v.audience)`: [3](#0-2) [4](#0-3) 

The only bindings actually enforced by `VerifyRequestJWT` are: signature validity, expiry/issued-at window, and equality between `claims.Digest` and the hash of the *currently presented* JSON-RPC request body: [5](#0-4) 

The gateway's `WorkflowMetadataHandler.Authorize` consumes this verified token and scopes authorization purely by `workflowID → authorizedKeys` membership and a global `jti` replay cache — it does not check `Issuer`/`Audience` against the specific target workflow/gateway/DON either: [6](#0-5) 

Because the signed payload's `digest` binds only to the JSON-RPC method+params (not to the target `workflowID`, DON, or gateway instance), and `Issuer`/`Audience` are never checked, a signature that is valid for one intended target/context can be presented and accepted for a different target/context that happens to (a) share an identical request digest and (b) list the same signer's key as authorized — exactly the same class of bug as the Teller report: a signature verification path that omits a domain-separation field the struct/claims already carry, enabling reuse outside the originally intended scope.

### Impact Explanation
Where the same signer key is authorized on multiple workflows/environments (a legitimate and expected topology for CRE HTTP-trigger workflows) and requests with identical params/digest exist across those scopes, a JWT minted/authorized for one target can be replayed to gain execution authorization on another target sharing that digest, without the workflow owner or infra ever intending the token to be valid there. This is a genuine authentication/authorization scoping weakness reachable from an unprivileged HTTP-trigger client, distinct from (and stronger than) simple `jti` replay, because the missing checks are structural (unused claim fields), not an edge-case bug.

### Likelihood Explanation
Moderate. Exploitation requires the attacker (or a legitimate but careless caller) to have a signer key authorized on more than one `workflowID`/gateway target and for two request bodies to hash identically (e.g., default/empty params, or shared trigger schemas across tenants/environments). This is plausible in practice because `CreateRequestJWT`'s digest is derived purely from method+params, and multi-workflow/multi-environment key reuse by the same organization is a realistic operational pattern.

### Recommendation
Have `VerifyRequestJWT` enforce `jwt.WithIssuer(...)` and `jwt.WithAudience(...)` against the expected target (e.g., set `Audience` to the specific `workflowID`/DON/gateway identifier at mint time, and require `VerifyRequestJWT`/`Authorize` to check that the token's `aud` matches the `workflowID` being authorized), mirroring the pattern already used in `jwt_based_auth.go`. Alternatively, fold the target `workflowID`/DON identifier into the signed `digest` computation so a token minted for one target cannot validate against another.

### Proof of Concept
1. Workflow owner `O` authorizes signer key `K` on two workflows, `W1` and `W2` (`authorizedKeys[W1]` and `authorizedKeys[W2]` both contain `K`) — a supported, legitimate configuration.
2. `O` (or an attacker with only `W1` access) calls `CreateRequestJWT` for a JSON-RPC request `R` with generic/default params, producing a token `T` whose `Digest` claim is `hash(method, params)`, signed by `K`; `T.Issuer/Audience` are left unset or set to `W1`.
3. Caller sends `T` with request `R` (same method/params) to the gateway targeting `W2` instead of `W1`. `WorkflowMetadataHandler.Authorize("W2", T, R)` calls `utils.VerifyRequestJWT` — signature verifies, `exp/iat` valid, `jti` unseen, and `claims.Digest == hash(R)` matches; `Issuer`/`Audience` are never compared to `"W2"`.
4. `Authorize` proceeds to check only `authorizedKeys["W2"]` for `K`, which succeeds because `K` is also authorized on `W2` — the token minted in the context of `W1` is accepted for `W2`, even though it was never scoped/intended for `W2`. [3](#0-2) [6](#0-5)

### Citations

**File:** core/utils/jwt.go (L168-216)
```go
func CreateRequestJWT[T any](req jsonrpc.Request[T], opts ...Option) (*jwt.Token, error) {
	// Apply options
	options := &jwtOptions{}
	for _, opt := range opts {
		opt(options)
	}

	expiryDuration := maxJWTExpiryDuration
	if options.expiryDuration != nil {
		expiryDuration = *options.expiryDuration
	}

	digest, err := req.Digest()
	if err != nil {
		return nil, err
	}

	var issuer string
	if options.issuer != nil {
		issuer = *options.issuer
	}

	var subject string
	if options.subject != nil {
		subject = *options.subject
	}

	var audience []string
	if options.audience != nil {
		audience = options.audience
	}

	now := time.Now()
	jti := uuid.New().String()

	claims := JWTClaims{
		Digest: "0x" + digest,
		RegisteredClaims: jwt.RegisteredClaims{
			ID:        jti,
			Issuer:    issuer,
			Subject:   subject,
			Audience:  jwt.ClaimStrings(audience),
			ExpiresAt: jwt.NewNumericDate(now.Add(expiryDuration)),
			IssuedAt:  jwt.NewNumericDate(now),
		},
	}

	return jwt.NewWithClaims(&SigningMethodEth{}, claims), nil
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

**File:** core/utils/jwt.go (L277-301)
```go
	reqDigest, err := req.Digest()
	if err != nil {
		return nil, gethcommon.Address{}, err
	}
	if verifiedClaims.ID == "" {
		return nil, gethcommon.Address{}, errors.New("JWT ID (jti) is required but missing")
	}
	if verifiedClaims.ExpiresAt == nil {
		return nil, gethcommon.Address{}, errors.New("expiredAt (exp) is required but missing")
	}
	if verifiedClaims.IssuedAt == nil {
		return nil, gethcommon.Address{}, errors.New("issuedAt (iat) is required but missing")
	}
	now := time.Now()
	issuedAt := verifiedClaims.IssuedAt
	if issuedAt.After(now.Add(issuedAtTolerance)) {
		return nil, gethcommon.Address{}, fmt.Errorf("issuedAt (iat) is too far in the future (beyond tolerance of %.0f seconds)", issuedAtTolerance.Seconds())
	}
	duration := verifiedClaims.ExpiresAt.Sub(verifiedClaims.IssuedAt.Time)
	if duration > maxExpiryDuration {
		return nil, gethcommon.Address{}, fmt.Errorf("token lifetime %.0f sec exceeds the maximum allowed %.0f sec. Reduce the gap between 'iat' and 'exp'", duration.Seconds(), maxExpiryDuration.Seconds())
	}
	if verifiedClaims.Digest != "0x"+reqDigest {
		return nil, gethcommon.Address{}, fmt.Errorf("claim digest '%s' does not match calculated request digest '0x%s'", verifiedClaims.Digest, reqDigest)
	}
```

**File:** core/capabilities/vault/jwt_based_auth.go (L258-269)
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
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-100)
```go
func (h *WorkflowMetadataHandler) Authorize(workflowID string, token string, req *jsonrpc.Request[json.RawMessage]) (*gateway.AuthorizedKey, error) {
	claims, signer, err := utils.VerifyRequestJWT(token, *req)
	if err != nil {
		h.lggr.Errorw("Failed to verify JWT", "error", err)
		return nil, err
	}

	if h.jwtCache.isReplay(claims.ID) {
		h.lggr.Warnw("JWT token has already been used", "workflowID", workflowID, "signer", signer.Hex(), "jti", claims.ID)
		return nil, errors.New("JWT token has already been used. Please generate a new one with new id (jti)")
	}

	keys, exists := h.authorizedKeys[workflowID]
	if !exists {
		h.lggr.Errorw("Workflow ID not found in authorized keys", "workflowID", workflowID)
		return nil, fmt.Errorf("workflow ID %s not found", workflowID)
	}
	key := gateway.AuthorizedKey{
		KeyType:   gateway.KeyTypeECDSAEVM,
		PublicKey: strings.ToLower(signer.Hex()),
	}
```
