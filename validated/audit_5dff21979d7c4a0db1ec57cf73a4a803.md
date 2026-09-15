This confirms all the claim's factual assertions. `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` are wired without any role wrapper — only `auth.Authenticate` [1](#0-0) , while sibling mutation routes use `auth.RequiresEditRole` [2](#0-1) . `RequiresEditRole` explicitly rejects `UserRoleView` and `UserRoleRun`, proving "view" role is lower-privileged and normally blocked from edit-only endpoints [3](#0-2) [4](#0-3) . The presenter unconditionally serializes `OutgoingToken` with no `omitempty`, unlike `IncomingToken` [5](#0-4) , and `Index`/`Show` both build this resource and return it directly [6](#0-5) .

Audit Report

## Title
Bridge `OutgoingToken` credential exposed in plaintext to unprivileged "view"-role users via unrestricted `GET /v2/bridge_types` endpoints - (File: core/web/router.go, core/web/bridge_types_controller.go, core/web/presenters/bridges.go)

## Summary
`BridgeTypesController.Index` and `.Show` are registered behind only `auth.Authenticate` with no role check, while `Create`, `Update`, and `Destroy` on the same resource are wrapped in `auth.RequiresEditRole`. Both read endpoints return a `BridgeResource` whose `OutgoingToken` field is serialized unconditionally (no `omitempty`), so any authenticated user — including one restricted to the lowest "view" role, which is explicitly excluded from edit-level actions — can read every bridge's outgoing authentication secret.

## Finding Description
The route table shows `bt.Index` and `bt.Show` registered with no role wrapper, in contrast to `bt.Create`, `bt.Update`, `bt.Destroy` which use `auth.RequiresEditRole`:
`core/web/router.go` L268-273.

`RequiresEditRole` demonstrates the intended privilege boundary by rejecting `UserRoleView` and `UserRoleRun`, meaning bridge mutation was deliberately restricted above "view":
`core/web/auth/auth.go` L217-234, and `UserRoleView` is a documented, real role: `core/sessions/user.go` L29-34.

`BridgeResource.OutgoingToken` has no `omitempty` and is populated directly from the stored `BridgeType.OutgoingToken` on every construction, whereas `IncomingToken` is `omitempty` and only populated at `Create` time:
`core/web/presenters/bridges.go` L10-41.

`Index` and `Show` both call `presenters.NewBridgeResource` and return it as the JSON:API response body without any redaction:
`core/web/bridge_types_controller.go` L112-146.

`OutgoingToken` is the live credential used by the node to authenticate itself when calling out to the bridge's external adapter (`core/bridges/bridge_type.go`), so it is a genuine secret rather than incidental metadata. Since `Index`/`Show` sit behind the same `authv2` group used generally for authenticated access (`auth.Authenticate`, requiring only a valid session or API token — no role check), the existing access controls (`RequiresEditRole`/`RequiresAdminRole`) that gate every other bridge-mutating action are simply absent here, and no field-level redaction exists to compensate.

## Impact Explanation
This is a credential-disclosure issue mapping to the "key/secret exfiltration" impact class. An operator provisioning a "view"-role account for read-only dashboard/monitoring purposes unintentionally grants that principal the ability to read the `OutgoingToken` of every configured bridge, which can be used to impersonate the node when calling the external adapter (or replay/misuse whatever the adapter checks on inbound calls from the node). It does not grant the ability to call back into the node itself, but it is a clear violation of the role-based access boundary the codebase establishes for bridge secrets elsewhere (matching the `IncomingToken`'s create-only exposure pattern).

## Likelihood Explanation
Exploitation requires only a valid low-privilege "view" role account/session or API token — a supported, documented role with no special conditions, no interaction with the bridge owner, and no timing constraints. Any multi-user deployment that follows the intended role model (granting "view" to non-admin users for monitoring) is exposed by default configuration.

## Recommendation
Wrap `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` in `auth.RequiresEditRole` (or `RequiresAdminRole`), matching the mutation endpoints; alternatively, remove `OutgoingToken` from `BridgeResource` for list/show responses (or make it `omitempty` and only populate on `Create`/rotation), consistent with the existing `IncomingToken` handling pattern.

## Proof of Concept
1. As an admin, create a user with role `view` (`POST /v2/users` with role `view`).
2. As an admin, create a bridge via `POST /v2/bridge_types`; note the returned `outgoingToken`.
3. Authenticate as the `view`-role user (session login or API token) and issue `GET /v2/bridge_types/<name>` or `GET /v2/bridge_types`.
4. Observe the JSON response includes `"outgoingToken": "<secret>"` per `core/web/presenters/bridges.go` L18, despite the route requiring no edit/admin role per `core/web/router.go` L269, L271 — confirming the disclosure.

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

**File:** core/web/auth/auth.go (L219-234)
```go
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

**File:** core/sessions/user.go (L29-34)
```go
const (
	UserRoleAdmin UserRole = "admin"
	UserRoleEdit  UserRole = "edit"
	UserRoleRun   UserRole = "run"
	UserRoleView  UserRole = "view"
)
```

**File:** core/web/presenters/bridges.go (L16-21)
```go
	// The IncomingToken is only provided when creating a Bridge
	IncomingToken          string       `json:"incomingToken,omitempty"`
	OutgoingToken          string       `json:"outgoingToken"`
	MinimumContractPayment *assets.Link `json:"minimumContractPayment"`
	UseConnectionManager   bool         `json:"useConnectionManager"`
	CreatedAt              time.Time    `json:"createdAt"`
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
