### Title
Unrestricted read access lets any authenticated (view-role) user enumerate bridge integration names/details - ([File: core/web/router.go])

### Summary
The CVE analog is a role/authorization gap, not the same root cause as the GitLab issue (which was a pure algorithmic-complexity DoS in template-name enumeration). In this codebase, `GET /v2/bridge_types/:BridgeName` is registered without any role gate, so any authenticated user — including the lowest-privilege `view` role, which cannot create/update/delete bridges — can brute-force bridge names one at a time and learn which integrations exist and their configuration (URL, confirmations, minimum contract payment). This mirrors the CVE's core pattern: a user who has some access but lacks privilege over a specific resource can enumerate resource names that should not be fully visible to them, and the request path carries no cost/rate control specific to that enumeration.

### Finding Description
In `core/web/router.go`, the `v2Routes` function wires up the bridge-types endpoints: [1](#0-0) 

Only `Create`, `Update`, and `Destroy` are wrapped with `auth.RequiresEditRole`. `Index` and `Show` have no role wrapper at all — they only require that the caller pass the generic `authv2` authentication middleware (session cookie or API token), which is satisfied by every role including the read-only `view` role: [2](#0-1) 

The `Show` handler itself performs a direct-name lookup with no additional access check tied to caller identity or role, and distinguishes "not found" vs "found" via HTTP status: [3](#0-2) 

This is confirmed by the existing test, which shows a 200 for an existing bridge and a 404 for a guessed name — precisely the oracle needed for brute-force enumeration: [4](#0-3) 

At the transport layer, the only rate limiting applied to this route is the generic "Authenticated" rate limit group applied to the whole `/v2` API surface: [5](#0-4) 

There is no endpoint-specific or complexity-aware throttling comparable to the dedicated login rate limiter used for unauthenticated `/sessions` brute-force protection: [6](#0-5) [7](#0-6) 

So a `view`-role user (the lowest privilege tier, intended only to observe run-level data) can iterate over candidate bridge names against `GET /v2/bridge_types/:BridgeName` at the generic authenticated-API rate limit and enumerate the full set of configured external adapter/bridge names and their non-secret metadata, despite having no edit rights over bridges.

### Impact Explanation
Impact is disclosure-only, not fund movement or privilege escalation: bridge type responses do not include the `IncomingToken` secret (that's only returned once at creation time in `Create`), so the direct leak is limited to bridge names, URLs, confirmation counts, and minimum contract payment. However, this still constitutes an authorization boundary violation: the codebase clearly intends bridge mutation to be edit-role-gated, but omitted an equivalent read-role gate on `Show`/`Index`, letting a `view`-role principal learn the node's external-adapter topology (internal/external URLs, naming conventions) that it is not otherwise entitled to inspect. This is a cross-role information-disclosure/enumeration issue analogous to the CVE's core flaw (project member without repository access enumerating template names it shouldn't see), scoped to node API roles as required.

### Likelihood Explanation
High likelihood of successful enumeration for any attacker holding valid `view`-role credentials (a legitimately low-privilege, already-authenticated account) — no special conditions, no timing side channel needed, and the response codes directly distinguish existing/non-existing names. The primary limiting factor is the generic authenticated rate limit, but that limit is shared across the whole API and not tuned to prevent brute-force name enumeration specifically.

### Recommendation
Gate `bt.Show` (and likely `bt.Index`) behind at least `auth.RequiresRunRole` or `auth.RequiresEditRole`, consistent with the mutation endpoints, so that `view`-role sessions/tokens cannot read bridge configuration. If broader visibility is intentional, add endpoint-specific throttling (similar to the `/sessions` unauthenticated rate limiter) to `GET /v2/bridge_types/:BridgeName` to blunt brute-force enumeration, and consider returning a uniform response (e.g., 403 for existing-but-unauthorized) that doesn't leak existence via 404 vs 200 for lower roles.

### Proof of Concept
1. Provision a user with `UserRoleView` (lowest privilege), obtain a session cookie or API token via `auth.AuthenticateByToken`/`AuthenticateBySession`.
2. Issue repeated `GET /v2/bridge_types/<guess>` requests with that view-role credential — no `auth.RequiresEditRole`/`RequiresRunRole` check exists on this route, so all requests succeed at the authentication layer.
3. Observe `200 OK` with full bridge metadata for real names (as in `TestBridgeController_Show`) and `404 Not Found` for guesses, enabling systematic enumeration of the node's configured bridges/integration names by an actor who is authenticated but has no edit/administrative rights over bridges.

Note: I could not find evidence in the indexed codebase of any per-route brute-force protection or role check specifically for `bt.Index`/`bt.Show` beyond what is shown above; if such protection exists elsewhere (e.g., in a reverse proxy or gateway config not present in this repo), it would mitigate this finding, but nothing in `core/web/router.go` or `bridge_types_controller.go` indicates it.

### Citations

**File:** core/web/router.go (L77-91)
```go
	rl := config.WebServer().RateLimit()
	api := engine.Group(
		"/",
		rateLimiter(
			rl.AuthenticatedPeriod(),
			rl.Authenticated(),
		),
		sessions.Sessions(auth.SessionName, sessionStore),
	)

	debugRoutes(app, api)
	healthRoutes(app, api)
	sessionRoutes(app, api)
	v2Routes(app, api)
	loopRoutes(app, api)
```

**File:** core/web/router.go (L207-218)
```go
func sessionRoutes(app chainlink.Application, r *gin.RouterGroup) {
	config := app.GetConfig()
	rl := config.WebServer().RateLimit()
	unauth := r.Group("/", rateLimiter(
		rl.UnauthenticatedPeriod(),
		rl.Unauthenticated(),
	))
	sc := NewSessionsController(app)
	unauth.POST("/sessions", sc.Create)
	auth := r.Group("/", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	auth.DELETE("/sessions", sc.Destroy)
}
```

**File:** core/web/router.go (L245-248)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
```

**File:** core/web/router.go (L268-273)
```go
		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
```

**File:** core/web/bridge_types_controller.go (L124-146)
```go
// Show returns the details of a specific Bridge.
func (btc *BridgeTypesController) Show(c *gin.Context) {
	ctx := c.Request.Context()
	name := c.Param("BridgeName")

	taskType, err := bridges.ParseBridgeName(name)
	if err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	bt, err := btc.App.BridgeORM().FindBridge(ctx, taskType)
	if errors.Is(err, sql.ErrNoRows) {
		jsonAPIError(c, http.StatusNotFound, errors.New("bridge not found"))
		return
	}
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	jsonAPIResponse(c, presenters.NewBridgeResource(bt), "bridge")
}
```

**File:** core/web/bridge_types_controller_test.go (L287-300)
```go
	resp, cleanup := client.Get("/v2/bridge_types/" + bt.Name.String())
	t.Cleanup(cleanup)
	assert.Equal(t, http.StatusOK, resp.StatusCode, "Response should be successful")

	var resource presenters.BridgeResource
	cltest.ParseJSONAPIResponse(t, resp, &resource)
	assert.Equal(t, bt.Name.String(), resource.Name, "should have the same name")
	assert.Equal(t, bt.URL.String(), resource.URL, "should have the same URL")
	assert.Equal(t, bt.Confirmations, resource.Confirmations, "should have the same Confirmations")

	resp, cleanup = client.Get("/v2/bridge_types/nosuchbridge")
	t.Cleanup(cleanup)
	assert.Equal(t, http.StatusNotFound, resp.StatusCode, "Response should be 404")
}
```

**File:** core/web/router_test.go (L127-156)
```go
func TestSessions_RateLimited(t *testing.T) {
	t.Parallel()

	ctx := t.Context()
	app := cltest.NewApplicationEVMDisabled(t)
	require.NoError(t, app.Start(ctx))

	router := web.Router(t, app, nil)
	ts := httptest.NewServer(router)
	defer ts.Close()

	client := clhttptest.NewTestLocalOnlyHTTPClient()
	input := `{"email":"brute@force.com", "password": "wrongpassword"}`

	for range 5 {
		request, err := http.NewRequestWithContext(ctx, http.MethodPost, ts.URL+"/sessions", bytes.NewBufferString(input))
		require.NoError(t, err)

		resp, err := client.Do(request)
		require.NoError(t, err)
		assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
	}

	request, err := http.NewRequestWithContext(ctx, http.MethodPost, ts.URL+"/sessions", bytes.NewBufferString(input))
	require.NoError(t, err)

	resp, err := client.Do(request)
	require.NoError(t, err)
	assert.Equal(t, 429, resp.StatusCode)
}
```
