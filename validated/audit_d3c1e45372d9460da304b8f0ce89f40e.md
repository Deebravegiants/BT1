## Finding

Chainlink node's OIDC login flow in `core/sessions/oidcauth/oidc.go` implements the OAuth2/OIDC authorization code flow but only protects it with a `state` parameter — it never generates, transmits, or verifies an OIDC `nonce`, and it does not use PKCE. This mirrors the root cause behind CVE-2024-12369/GHSA-5565-3c98-g6jc (CWE-345, insufficient verification of the authenticity of the authorization response), where the missing binding between the authentication request and the returned ID Token/authorization code enables authorization code injection.

### Title
Missing nonce binding in OIDC authentication flow enables authorization code/ID token injection - (File: core/sessions/oidcauth/oidc.go)

### Summary
The `oidcAuthenticator` (unprivileged, unauthenticated-by-design login flow reachable at `/signin`/token-exchange endpoints) issues an OAuth2 authorization request with only a `state` value and no `nonce`, then on callback verifies the returned ID token without checking any nonce claim, relying solely on `state` equality to the session-stored value.

### Finding Description
`handleSignIn` generates a random `state`, stores it in the gin session, and redirects to the identity provider using only `state` (no `nonce` parameter is added to the authorization request): [1](#0-0) 

`handleTokenExchange` accepts a `code`/`state` pair posted by the frontend, checks `state` against the session value, exchanges the `code` for tokens, and verifies the ID token — but at no point does it check a `nonce` claim inside the verified ID token against a value tied to the original authentication request: [2](#0-1) 

The `oidc.Config` used for verification only sets `ClientID`, with no nonce enforcement configured, and the `go-oidc` library's `Verifier.Verify()` call does not automatically enforce nonce matching — that responsibility is left entirely to the relying party, which chainlink does not implement here: [3](#0-2) [4](#0-3) 

Per the OpenID Connect Core spec and the OAuth 2.0 Security Best Current Practice, `state` alone provides CSRF protection for the redirect endpoint, but `nonce` is the mechanism that cryptographically binds a specific ID Token/authorization code to the authentication transaction that produced it, preventing replay or injection of a code/token obtained through a different transaction (e.g. via IdP mix-up, MitM-swapped redirect responses, or phishing flows where an attacker's own valid code is substituted into a victim's browser). There is no `CodeVerifier`/PKCE usage either, confirmed by the absence of any `code_verifier`/`code_challenge` references in the codebase, so no alternative binding mechanism compensates for the missing nonce check.

### Impact Explanation
If exploited, this class of flaw allows an attacker to inject a previously-obtained authorization code/ID token into a victim's authentication flow, causing the client (the chainlink node's web server) to establish a session under attacker-controlled or confused identity/claims. Given that the resulting session directly determines the RBAC role assigned via `IDClaimsToUserRole` and is used for subsequent authenticated node-API access, a successful injection could lead to unauthorized session establishment with elevated (e.g. Admin) roles.

### Likelihood Explanation
Exploitation requires an attacker to intercept or otherwise obtain a valid authorization code/ID token (e.g. MitM on network path to IdP, phishing, or IdP-side mix-up) and then get it delivered into a victim's flow — consistent with the CVSS vector of the underlying advisory (`AC:H`, `UI:R`). It's not trivially exploitable by a purely network-external actor without additional preconditions, but the underlying node code provides no defense-in-depth (nonce check) that the OIDC spec recommends specifically to mitigate this scenario.

### Recommendation
Add a `nonce` to the authorization request in `handleSignIn` (store alongside `state` in the session), and after verifying the ID token in `handleTokenExchange`, extract the `nonce` claim and compare it (constant-time) against the session-stored value before establishing the session—rejecting the exchange on mismatch. Consider also adopting PKCE (`code_verifier`/`code_challenge`) for the authorization code exchange as additional defense-in-depth.

### Proof of Concept
1. Attacker completes their own legitimate OIDC login against the same IdP/client, obtaining a valid `code` (and resulting `id_token`) tied to their own identity/claims.
2. Attacker gets a victim's browser (already having an active chainlink session state from a prior `/signin` redirect, or via a crafted phishing/MitM interaction) to submit the attacker's `code` value (paired with a `state` the attacker manages to align with the victim's session, e.g. via network-level interception of the redirect) to the token-exchange endpoint handled by `handleTokenExchange`.
3. Because only `state` is checked and no `nonce` binds the returned ID token to the specific authentication transaction, the exchange in `oidc.go` lines 163-219 succeeds and creates an `oidc_sessions` row and cookie for the victim's browser using claims potentially not originating from the transaction the victim initiated.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L97-118)
```go
	var provider *oidc.Provider
	var oidcConfig *oidc.Config
	var oauth2Config *oauth2.Config

	ctx := context.Background()
	// Initialize provider based on config domain, this contains a blocking call to as part of the OpenID Connect discovery process
	provider, err := oidc.NewProvider(ctx, oidcCfg.ProviderURL())
	if err != nil {
		log.Fatalf("Failed to get provider: %v", err)
	}

	// Construct oidc and oath callback configs for oidcAuth struct
	oidcConfig = &oidc.Config{
		ClientID: oidcCfg.ClientID(),
	}
	oauth2Config = &oauth2.Config{
		ClientID:     oidcCfg.ClientID(),
		ClientSecret: oidcCfg.ClientSecret(),
		Endpoint:     provider.Endpoint(),
		RedirectURL:  oidcCfg.RedirectURL(),
		Scopes:       []string{oidc.ScopeOpenID, "profile", "email", oidcCfg.ClaimName()},
	}
```

**File:** core/sessions/oidcauth/oidc.go (L147-161)
```go
func (oi *oidcAuthenticator) handleSignIn(c *gin.Context) {
	// generate state and store on session
	state := oi.generateState()
	session := sessions.Default(c)
	session.Set("state", state)
	err := session.Save()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save session"})
		return
	}

	// redirect to provider
	url := oi.oauth2Config.AuthCodeURL(state, oauth2.AccessTypeOffline)
	c.Redirect(http.StatusFound, url)
}
```

**File:** core/sessions/oidcauth/oidc.go (L163-219)
```go
func (oi *oidcAuthenticator) handleTokenExchange(c *gin.Context) {
	// parse and validate the incoming JSON request
	var req ExchangeTokenRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ExchangeTokenResponse{
			Success: false,
			Message: "Invalid request: " + err.Error(),
		})
		return
	}

	// check state matches stored value on the session
	ginSession := sessions.Default(c)
	storedState := ginSession.Get("state")
	if storedState == nil || req.State != storedState.(string) {
		c.JSON(http.StatusBadRequest, ExchangeTokenResponse{
			Success: false,
			Message: "Invalid state parameter",
		})
		return
	}
	ginSession.Delete("state")

	// Begin token exchange to retrieve attested claims of authenticated user
	ctx := context.Background()
	oauth2Token, err := oi.oauth2Config.Exchange(ctx, req.Code)
	if err != nil {
		oi.lggr.Errorf("Failed to exchange token: %v", err)
		c.JSON(http.StatusInternalServerError, ExchangeTokenResponse{
			Success: false,
			Message: "OIDC exchange failed",
		})
		return
	}

	// Request token from provider for claims lookup and verification
	rawIDToken, ok := oauth2Token.Extra("id_token").(string)
	if !ok {
		oi.lggr.Errorf("No id_token field in oauth2 token: %v", err)
		c.String(http.StatusInternalServerError, "Missing id_token field in response")
		return
	}

	// Verify claim and retrieve attested user id claims
	idToken, err := oi.provider.Verifier(oi.oidcConfig).Verify(ctx, rawIDToken)
	if err != nil {
		oi.lggr.Errorf("Failed to verify ID token: %v", err)
		c.String(http.StatusInternalServerError, "Failed to verify ID token")
		return
	}

	var claims map[string]any
	if err = idToken.Claims(&claims); err != nil {
		oi.lggr.Errorf("Failed to parse OIDC return claims: %v", err)
		c.String(http.StatusInternalServerError, "Failed to parse OIDC return claims")
		return
	}
```
