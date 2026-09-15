Audit Report

## Title
Bridge `outgoingToken` credential is exposed in plaintext to low-privilege "view" role users via `/v2/bridge_types` API and GraphQL - ([File: core/web/router.go])

## Summary
The `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` REST endpoints, and the GraphQL `bridge`/`bridges` queries, return each bridge's `OutgoingToken` — a plaintext secret used by the node to authenticate to external adapters — to any authenticated user, including the lowest-privilege "view" role. No role gate or redaction exists on these read paths, while all mutating bridge routes are correctly restricted with `auth.RequiresEditRole`.

## Finding Description
`v2Routes` registers `GET /bridge_types` and `GET /bridge_types/:BridgeName` with only the base session/token authentication middleware and no role wrapper, unlike the sibling `POST`/`PATCH`/`DELETE` bridge routes which use `auth.RequiresEditRole`: [1](#0-0) . `BridgeTypesController.Index` and `.Show` fetch the ORM `BridgeType` and pass it straight to `presenters.NewBridgeResource`, which unconditionally copies `OutgoingToken` (no `omitempty`, no masking) into the JSON:API response — contrasted with `IncomingToken`, which is deliberately only populated at creation time: [2](#0-1) , [3](#0-2) . On the GraphQL side, `Resolver.Bridge`/`Bridges` only call `authenticateUser`, which merely checks for a valid session (equivalent to "view" role) rather than `authenticateUserCanEdit`: [4](#0-3) , [5](#0-4) , and `BridgeResolver.OutgoingToken()` returns the raw token: [6](#0-5) . This is confirmed as the actual (and deliberately tested) behavior by the RBAC test matrix, which marks `GET /v2/bridge_types` and `GET /v2/bridge_types/MOCK` as `viewOnlyAllowed: true` and is asserted to succeed for a `UserRoleView` session in `TestRBAC_Routemap_ViewOnly`: [7](#0-6) , [8](#0-7) . The existing `RequiresEditRole`/`authenticateUserCanEdit` gates, which do enforce at least edit role on mutating bridge routes, are simply never applied to the read paths that leak the secret: [9](#0-8) , [10](#0-9) .

## Impact Explanation
A session/API token holder with only the "view" role — the lowest role in Chainlink's RBAC hierarchy, intended for read-only/monitoring access — can retrieve every configured bridge's `OutgoingToken` via a simple authenticated `GET /v2/bridge_types` call or the GraphQL `bridges` query. Since this token is the credential the node uses to authenticate itself to the external bridge adapter, its disclosure lets a view-role principal impersonate the node to that adapter or otherwise misuse the token wherever the adapter trusts it — a concrete secret-exfiltration impact (CWE-522) that crosses an RBAC privilege boundary the codebase otherwise enforces (mutations require edit role; `IncomingToken` is deliberately withheld outside of creation). This does not directly move funds or execute jobs, so it is a secret-disclosure / privilege-boundary bug of moderate-to-high severity depending on how the external adapter trusts the token.

## Likelihood Explanation
Likelihood is high wherever an operator provisions "view"-role accounts (auditors, dashboards, monitoring integrations, third-party read access) — a supported and documented use case for that role. No additional secret or race condition is needed; a single authenticated GET/GraphQL request with view credentials fully discloses the token, and there is no rate limiting or redaction to mitigate repeated retrieval.

## Recommendation
Restrict `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` (and GraphQL `bridge`/`bridges`) to require at least `edit`/`run` role via `auth.RequiresEditRole`/`authenticateUserCanEdit`, or strip/mask `OutgoingToken` from list/show responses for view-role callers, consistent with how `IncomingToken` is only exposed at creation time. Consider making `OutgoingToken` `omitempty` and only revealing it through an explicit privileged "reveal" action.

## Proof of Concept
1. Create a Chainlink node user/API token with role `view` (e.g., via `chainlink admin users create`/`ChangeRole` to `view`).
2. As that view-role session, call `GET /v2/bridge_types` or issue GraphQL query `{ bridges { results { name outgoingToken } } }`.
3. Observe the response includes `outgoingToken` in plaintext, as demonstrated by `core/web/bridge_types_controller_test.go` (Show handler returns full `BridgeResource` including `OutgoingToken`) and `core/web/resolver/bridge_test.go::Test_Bridges` (GraphQL response includes `"outgoingToken": "outgoingToken"`), combined with the RBAC fixture confirming `viewOnlyAllowed: true` for these routes in `core/web/auth/auth_test.go`.

### Citations

**File:** core/web/router.go (L268-273)
```go
		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
```

**File:** core/web/presenters/bridges.go (L10-42)
```go
// BridgeResource represents a Bridge JSONAPI resource.
type BridgeResource struct {
	JAID
	Name          string `json:"name"`
	URL           string `json:"url"`
	Confirmations uint32 `json:"confirmations"`
	// The IncomingToken is only provided when creating a Bridge
	IncomingToken          string       `json:"incomingToken,omitempty"`
	OutgoingToken          string       `json:"outgoingToken"`
	MinimumContractPayment *assets.Link `json:"minimumContractPayment"`
	UseConnectionManager   bool         `json:"useConnectionManager"`
	CreatedAt              time.Time    `json:"createdAt"`
}

// GetName implements the api2go EntityNamer interface
func (r BridgeResource) GetName() string {
	return "bridges"
}

// NewBridgeResource constructs a new BridgeResource
func NewBridgeResource(b bridges.BridgeType) *BridgeResource {
	return &BridgeResource{
		// Uses the name as the id...Should change this to the id
		JAID:                   NewJAID(b.Name.String()),
		Name:                   b.Name.String(),
		URL:                    b.URL.String(),
		Confirmations:          b.Confirmations,
		OutgoingToken:          b.OutgoingToken,
		MinimumContractPayment: b.MinimumContractPayment,
		UseConnectionManager:   b.UseConnectionManager,
		CreatedAt:              b.CreatedAt,
	}
}
```

**File:** core/web/bridge_types_controller.go (L112-146)
```go
func (btc *BridgeTypesController) Index(c *gin.Context, size, page, offset int) {
	ctx := c.Request.Context()
	bridges, count, err := btc.App.BridgeORM().BridgeTypes(ctx, offset, size)

	resources := make([]presenters.BridgeResource, 0, len(bridges))
	for _, bridge := range bridges {
		resources = append(resources, *presenters.NewBridgeResource(bridge))
	}

	paginatedResponse(c, "Bridges", size, page, resources, count, err)
}

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

**File:** core/web/resolver/query.go (L27-48)
```go
// Bridge retrieves a bridges by name.
func (r *Resolver) Bridge(ctx context.Context, args struct{ ID graphql.ID }) (*BridgePayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}

	name, err := bridges.ParseBridgeName(string(args.ID))
	if err != nil {
		return nil, err
	}

	bridge, err := r.App.BridgeORM().FindBridge(ctx, name)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return NewBridgePayload(bridge, err), nil
		}

		return nil, err
	}

	return NewBridgePayload(bridge, nil), nil
}
```

**File:** core/web/resolver/auth.go (L11-17)
```go
// Authenticates the user from the session cookie, presence of user inherently provides 'view' access.
func authenticateUser(ctx context.Context) error {
	if _, ok := auth.GetGQLAuthenticatedSession(ctx); !ok {
		return unauthorizedError{}
	}
	return nil
}
```

**File:** core/web/resolver/auth.go (L31-43)
```go
// Authenticates the user from the session cookie and asserts at least 'edit' role.
func authenticateUserCanEdit(ctx context.Context) error {
	session, ok := auth.GetGQLAuthenticatedSession(ctx)
	if !ok {
		return unauthorizedError{}
	}
	switch session.User.Role {
	case sessions.UserRoleView, sessions.UserRoleRun:
		return RoleNotPermittedError{session.User.Role}
	default:
	}
	return nil
}
```

**File:** core/web/resolver/bridge.go (L52-55)
```go
// OutgoingToken resolves the bridge's outgoing token.
func (r *BridgeResolver) OutgoingToken() string {
	return r.bridge.OutgoingToken
}
```

**File:** core/web/auth/auth_test.go (L227-231)
```go
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
	{"DELETE", "/v2/bridge_types/MOCK", false, false, true},
```

**File:** core/web/auth/auth_test.go (L484-532)
```go
func TestRBAC_Routemap_ViewOnly(t *testing.T) {
	t.Parallel()
	app := cltest.NewApplicationEVMDisabled(t)
	require.NoError(t, app.Start(t.Context()))

	router := web.Router(t, app, nil)
	ts := httptest.NewServer(router)
	defer ts.Close()

	// Create a test run user to work with
	u := &cltest.User{Role: sessions.UserRoleView}
	client := app.NewHTTPClient(u)

	// Assert all view only routes
	for i, route := range routesRolesMap {
		t.Run(fmt.Sprintf("%d-%s-%s", i, route.verb, route.path), func(t *testing.T) {
			t.Parallel()
			var resp *http.Response
			var cleanup func()

			switch route.verb {
			case "GET":
				resp, cleanup = client.Get(route.path)
			case "POST":
				resp, cleanup = client.Post(route.path, nil)
			case "DELETE":
				resp, cleanup = client.Delete(route.path)
			case "PATCH":
				resp, cleanup = client.Patch(route.path, nil)
			case "PUT":
				resp, cleanup = client.Put(route.path, nil)
			default:
				t.Fatalf("Unknown HTTP verb %s\n", route.verb)
			}
			defer cleanup()

			// If this route only allows view only, don't expect an unauthorized response
			switch {
			case route.viewOnlyAllowed:
				assert.NotEqual(t, http.StatusUnauthorized, resp.StatusCode)
				assert.NotEqual(t, http.StatusForbidden, resp.StatusCode)
			case !route.EditAllowed:
				assert.Equal(t, http.StatusForbidden, resp.StatusCode)
			default:
				assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
			}
		})
	}
}
```

**File:** core/web/auth/auth.go (L217-234)
```go
// RequiresEditRole extracts the user object from the context, and asserts the user's role is at least
// 'edit'
func RequiresEditRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView || user.Role == clsessions.UserRoleRun {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}
```
