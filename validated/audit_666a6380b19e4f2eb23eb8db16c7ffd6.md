The claim is fully confirmed by the code. `bt.Index` and `bt.Show` in `core/web/router.go` are registered without any role gate — only wrapped in `paginatedRequest`/left bare, unlike `Create`/`Update`/`Destroy` which use `auth.RequiresEditRole` [1](#0-0) . `RequiresEditRole` explicitly blocks `UserRoleView` and `UserRoleRun`, confirming that a `view`-role authenticated session would otherwise be barred from write endpoints but is not barred from `GET /v2/bridge_types` or `GET /v2/bridge_types/:BridgeName` [2](#0-1) . `NewBridgeResource` unconditionally includes `OutgoingToken` in the JSON output for both `Index` and `Show`, with no redaction based on role, while `IncomingToken` is deliberately omitted except at creation via manual assignment in `Create` [3](#0-2) [4](#0-3) . The `authv2` group only requires successful session/token authentication (any role), not a minimum role, before reaching `bt.Index`/`bt.Show` [5](#0-4) .

This matches the required validation checks: exact file/line references are accurate, root cause (missing role wrapper vs. sibling write endpoints) is clear, exploit path only needs a `view`-role session/token (an unprivileged authenticated actor, which is in-scope since it's not admin/operator access), and impact is concrete secret disclosure (`OutgoingToken`, a bridge integration secret used to authenticate response callbacks) to an underprivileged caller. `SECURITY.md` in this repo covers a generic Immunefi exclusion template and does not exclude this class of authenticated low-privilege secret disclosure.

Audit Report

## Title
Missing role-based access control on Bridge Show/Index endpoints exposes bridge `OutgoingToken` secrets to low-privilege authenticated users - (File: core/web/router.go)

## Summary
`GET /v2/bridge_types` (`Index`) and `GET /v2/bridge_types/:BridgeName` (`Show`) are registered in `v2Routes` without any minimum-role wrapper, unlike the sibling `Create`/`Update`/`Destroy` routes on the same resource which require `auth.RequiresEditRole`. Because `presenters.NewBridgeResource` always serializes `OutgoingToken` in the response, any authenticated user — including the lowest-privilege `UserRoleView` — can read every bridge's `OutgoingToken` via these unauthenticated-for-role GET endpoints.

## Finding Description
In `v2Routes`, bridge write operations are gated with `auth.RequiresEditRole(bt.Create)`, `auth.RequiresEditRole(bt.Update)`, `auth.RequiresEditRole(bt.Destroy)`, but `authv2.GET("/bridge_types", paginatedRequest(bt.Index))` and `authv2.GET("/bridge_types/:BridgeName", bt.Show)` have no role wrapper, only the base `authv2` group's generic `auth.Authenticate` middleware (session or token, any role) [1](#0-0) . `RequiresEditRole` explicitly rejects `UserRoleView` and `UserRoleRun` [2](#0-1) , confirming these are meant to be treated as more privileged operations than plain read access — but no equivalent minimum-role check exists on the read paths. `BridgeTypesController.Show` and `Index` both call `presenters.NewBridgeResource`, which unconditionally sets `OutgoingToken` on the response struct with `json:"outgoingToken"` (no `omitempty`, no role check) [6](#0-5) [7](#0-6) [3](#0-2) . This contrasts with `IncomingToken`, which is tagged `omitempty` and only populated manually in `Create` [4](#0-3) , demonstrating the codebase's own design intent to treat bridge tokens as sensitive and role-restricted — an intent not carried through to the read endpoints.

## Impact Explanation
Any authenticated user holding only the `view` role (the lowest role in the RBAC hierarchy enforced by `RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole`) can enumerate all configured bridges and their `OutgoingToken` secrets via `GET /v2/bridge_types` or targeted `GET /v2/bridge_types/:BridgeName` requests. The `OutgoingToken` is used by the Chainlink node to authenticate itself to external bridge adapters/webhooks; its disclosure to an unprivileged reader constitutes unauthorized secret exfiltration, breaking the access boundary the API otherwise enforces (write ops require `edit`). This maps to the in-scope "key/secret exfiltration" impact category.

## Likelihood Explanation
High. Exploitation requires only a valid `view`-role API token or session — a normal, low-privilege credential tier that Chainlink node operators commonly provision for read-only/monitoring access. No race conditions, timing, or special preconditions are needed; a single authenticated `GET` request suffices, and the behavior is deterministic and repeatable.

## Recommendation
Wrap `bt.Index` and `bt.Show` with `auth.RequiresEditRole` (or an equivalent minimum-role check) to match the access level required for the other bridge management endpoints, or strip/redact `OutgoingToken` from `BridgeResource` for callers below the `edit` role, mirroring the existing `IncomingToken` redaction pattern (`omitempty`, populated only where appropriate).

## Proof of Concept
1. Provision a user/API token with `clsessions.UserRoleView`.
2. Authenticate with that credential and send `GET /v2/bridge_types` (or `GET /v2/bridge_types/:BridgeName` for a known bridge name).
3. Observe the JSON response body includes `"outgoingToken"` for each bridge — succeeding despite the fact that the same credential receives `401 Unauthorized` on `POST/PATCH/DELETE /v2/bridge_types*` due to `auth.RequiresEditRole`.
4. Compare against `router.go` lines 268-273 to confirm the asymmetry between read and write route role-gating.

### Citations

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

**File:** core/web/bridge_types_controller.go (L98-99)
```go
	resource := presenters.NewBridgeResource(*bt)
	resource.IncomingToken = bta.IncomingToken
```

**File:** core/web/bridge_types_controller.go (L112-122)
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
