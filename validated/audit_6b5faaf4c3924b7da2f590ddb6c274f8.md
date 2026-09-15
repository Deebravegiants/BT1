This matches the report's claims exactly. Let me verify the router registration and the RBAC test.All findings are confirmed by direct code inspection. The route registration, the presenter, the controller, and the RBAC test all match exactly as described.

Audit Report

## Title
Bridge outgoing authentication token exposed to Viewer-role users via `GET /v2/bridge_types/:BridgeName` - (File: core/web/bridge_types_controller.go)

## Summary
The `GET /v2/bridge_types/:BridgeName` route is registered without any role-restriction middleware, while sibling `Create`/`Update`/`Destroy` routes require `auth.RequiresEditRole`. The `Show` handler serializes the bridge via `presenters.NewBridgeResource`, which unconditionally includes the `OutgoingToken` secret field (no `omitempty`, unlike `IncomingToken`), so any authenticated user—including one with only `UserRoleView`—can retrieve a bridge's outgoing authentication secret.

## Finding Description
In `core/web/router.go`, the bridge routes are: `authv2.GET("/bridge_types/:BridgeName", bt.Show)` with no wrapper, versus `authv2.PATCH(...)`, `authv2.DELETE(...)`, and `authv2.POST("/bridge_types", ...)` which are wrapped in `auth.RequiresEditRole`. [1](#0-0) 

`BridgeTypesController.Show` fetches the bridge and returns `presenters.NewBridgeResource(bt)` directly. [2](#0-1) 

`BridgeResource.OutgoingToken` has no `omitempty` and is unconditionally populated from `b.OutgoingToken` in `NewBridgeResource`, in contrast to `IncomingToken`, which is commented as "only provided when creating a Bridge" and tagged with `omitempty`. [3](#0-2) 

The project's own RBAC route test (`routesRolesMap` in `auth_test.go`) explicitly marks `GET /v2/bridge_types/MOCK` as `viewOnlyAllowed: true`, and `TestRBAC_Routemap_ViewOnly` asserts that a `UserRoleView` session must not receive `401`/`403` on these routes — confirming the endpoint is intentionally reachable by View-role sessions. [4](#0-3) [5](#0-4) 

The role hierarchy in `core/web/auth/auth.go` shows `RequiresEditRole` blocks `UserRoleView` and `UserRoleRun`, while no such wrapper exists for `Show`; only the generic `Authenticate` middleware (session cookie or API token) gates the route, which accepts any valid user regardless of role, including `UserRoleView`. [6](#0-5) 

This is a genuine broken access control: the code path, absent role gating, unconditionally returns a live outbound-authentication secret to any authenticated caller regardless of role.

## Impact Explanation
This maps to CWE-200 / secret exfiltration in scope for Chainlink node API vulnerabilities: a low-privilege (`UserRoleView`) authenticated user can read the `OutgoingToken` for any named bridge — a secret Chainlink uses to authenticate outbound calls to the external bridge adapter. Since bridge names are enumerable via the equally unrestricted `GET /v2/bridge_types` index route, a Viewer can harvest all bridge outgoing tokens in the node, which could then be used to impersonate the Chainlink node when calling the adapter or otherwise abuse the exposed credential.

## Likelihood Explanation
High and trivially repeatable: no special privilege beyond a valid low-tier account (View role) is needed; the request is a single unauthenticated-role-gated `GET`, and the project's own test suite documents the endpoint's view-only reachability, confirming the behavior is not accidental/edge-case but reflects an actual gap in role enforcement for this specific field.

## Recommendation
Wrap `GET /bridge_types/:BridgeName` (and consider the `Index` route too) with `auth.RequiresEditRole`, or strip/redact `OutgoingToken` from `BridgeResource` for non-Edit/Admin roles by adding `omitempty` and only populating it for privileged requesters (mirroring the existing `IncomingToken` creation-only treatment).

## Proof of Concept
1. Create a bridge (as Admin/Edit) with a known `OutgoingToken`.
2. Create a node user with `Role: sessions.UserRoleView` and authenticate (session or API token).
3. Issue `GET /v2/bridge_types/<bridge-name>` as that Viewer.
4. Observe HTTP 200 with JSON body containing `"outgoingToken": "<secret>"`, confirming disclosure to a Viewer-role account — reproducible directly via the existing `TestRBAC_Routemap_ViewOnly` test in `core/web/auth/auth_test.go`, which already asserts non-401/403 for this exact route under `UserRoleView`.

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

**File:** core/web/presenters/bridges.go (L10-41)
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
```

**File:** core/web/auth/auth_test.go (L227-231)
```go
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
	{"DELETE", "/v2/bridge_types/MOCK", false, false, true},
```

**File:** core/web/auth/auth_test.go (L484-524)
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
