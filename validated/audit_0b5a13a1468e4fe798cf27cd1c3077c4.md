All checks confirm the claim. `GET /v2/bridge_types` (Index) and `GET /v2/bridge_types/:BridgeName` (Show) are registered with **no role wrapper** — only base session/token authentication — while write endpoints (`Create`, `Update`, `Destroy`) require `RequiresEditRole`, as shown in `core/web/router.go` lines 269-273. This means any authenticated user, including the lowest-privileged `UserRoleView` role, can call these read endpoints and receive `presenters.BridgeResource` with `OutgoingToken` populated unconditionally, since the presenter has no `omitempty` or masking logic for that field, unlike `IncomingToken`. This is a genuine, code-verified over-disclosure: a "view"-only credential holder can obtain a secret which is otherwise supposed to be only shown at bridge creation, and that secret is a live bearer credential to an external adapter. This is not caused by leaked credentials, misconfiguration, or operator/admin access — it's exploitable by any low-privilege authenticated API user by design of the route wiring, matching the required impact category (key/secret exfiltration accessible to under-privileged actors).

Audit Report

## Title
Bridge `OutgoingToken` secret is returned unmasked to any authenticated user (including view-only role) on every bridge list/show/update/delete response - ([File: core/web/presenters/bridges.go])

## Summary
`BridgeType.OutgoingToken`, a persisted bearer secret used to authenticate the node to an external adapter, is unconditionally serialized in plaintext by `presenters.NewBridgeResource` and returned by `GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, `PATCH`, and `DELETE`. Critically, the `Index` and `Show` routes require only base authentication with no role gate, so even a `UserRoleView` (lowest-privileged) API/session user can read every bridge's `OutgoingToken` in plaintext.

## Finding Description
`BridgeType.OutgoingToken` is generated via `utils.NewSecret(24)` at creation and persisted as `db:"outgoing_token"` [1](#0-0) . The presenter `BridgeResource` marks `IncomingToken` with `json:"incomingToken,omitempty"` (populated only at creation) but has no such guard for `OutgoingToken` (`json:"outgoingToken"`), so it is always emitted [2](#0-1) . `NewBridgeResource` copies `b.OutgoingToken` directly into the response struct with no masking [3](#0-2) . `Index`, `Show`, `Update`, and `Destroy` controller actions all call `presenters.NewBridgeResource(bt)` on data fetched via `FindBridge`/`BridgeTypes`, re-emitting the full secret every time [4](#0-3) [5](#0-4) .

Critically, route registration shows `authv2.GET("/bridge_types", paginatedRequest(bt.Index))` and `authv2.GET("/bridge_types/:BridgeName", bt.Show)` have **no** `auth.RequiresEditRole`/`RequiresRunRole`/`RequiresAdminRole` wrapper, unlike the write actions (`Create`, `Update`, `Destroy`) which are wrapped with `auth.RequiresEditRole` [6](#0-5) . This means any authenticated session or API-token user — regardless of role, including `UserRoleView` — can call the read endpoints and receive the plaintext `OutgoingToken`. The GraphQL schema similarly exposes `outgoingToken: String!` as non-nullable on every `Bridge` query [7](#0-6) . The existing presenter unit test confirms this is the current, intentional behavior of the code as written [8](#0-7) .

This breaks the implicit security assumption that secrets like `OutgoingToken` (analogous to `IncomingToken`, which is properly one-time/creation-only) should not be persistently viewable, and specifically that role-based access control (`RequiresEditRole` etc.) meaningfully restricts sensitive data exposure — here the read paths bypass any such gate entirely.

## Impact Explanation
`OutgoingToken` is the bearer credential the node uses to authenticate itself to the bridge's external adapter. Any authenticated user with only "view" privileges (the lowest role in Chainlink's RBAC) can retrieve this live secret for every configured bridge via `GET /v2/bridge_types`, enabling impersonation of the node to the external adapter or further misuse of that credential — this is a legitimate secret exfiltration finding, exceeding the intended privilege boundary (view-only users should not have access to data equivalent to edit/admin-controlled secrets).

## Likelihood Explanation
Trivially and repeatably exploitable: any authenticated client with a valid session cookie or API token — with no elevated role required, since `Index`/`Show` have no role wrapper — can issue a single unauthenticated-in-privilege-terms `GET` request and receive the token in the default response shape, with no rate limiting or special conditions beyond normal authentication.

## Recommendation
- Restrict `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` to at least `RequiresEditRole` (or higher), consistent with the write actions on the same resource, to close the role-bypass exposure.
- Additionally, treat `OutgoingToken` like `IncomingToken`: only return it once at bridge creation (`omitempty` on the presenter), and mask/omit it on subsequent `Index`, `Show`, `Update`, and `Destroy` responses and in the GraphQL `Bridge` type.
- If the token must be surfaced later for rotation/troubleshooting, gate it behind an explicit "reveal" action restricted to `RequiresAdminRole` with audit logging.

## Proof of Concept
1. Create a user with `UserRoleView` (lowest privilege) via the admin API/CLI, or authenticate as any existing session/API-token user.
2. As that view-role user, issue `GET /v2/bridge_types` (or `GET /v2/bridge_types/:BridgeName` for a known bridge) against a node with at least one configured bridge.
3. Observe the JSON:API response includes `"outgoingToken": "<plaintext-secret>"` for each bridge — confirmed by `presenters.NewBridgeResource` behavior and the existing test fixture in `core/web/presenters/bridges_test.go`.
4. Confirm route-level lack of role restriction by inspecting `core/web/router.go` lines 269 and 271, where `bt.Index` and `bt.Show` are registered without any `auth.RequiresXRole` wrapper, in contrast to `bt.Create`/`bt.Update`/`bt.Destroy` which use `auth.RequiresEditRole`.
5. Use the captured `outgoingToken` to authenticate as the node when calling the bridge's configured external adapter URL.

### Citations

**File:** core/bridges/bridge_type.go (L57-68)
```go
type BridgeType struct {
	Name                   BridgeName    `db:"name"`
	URL                    models.WebURL `db:"url"`
	Confirmations          uint32        `db:"confirmations"`
	IncomingTokenHash      string        `db:"incoming_token_hash"`
	Salt                   string        `db:"salt"`
	OutgoingToken          string        `db:"outgoing_token"`
	MinimumContractPayment *assets.Link  `db:"minimum_contract_payment"`
	CreatedAt              time.Time     `db:"created_at"`
	UpdatedAt              time.Time     `db:"updated_at"`
	UseConnectionManager   bool          `db:"use_connection_manager" json:"useConnectionManager"`
}
```

**File:** core/web/presenters/bridges.go (L10-22)
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
```

**File:** core/web/presenters/bridges.go (L29-41)
```go
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

**File:** core/web/bridge_types_controller.go (L111-146)
```go
// Index lists Bridges, one page at a time.
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

**File:** core/web/bridge_types_controller.go (L148-192)
```go
// Update can change the restricted attributes for a bridge
func (btc *BridgeTypesController) Update(c *gin.Context) {
	ctx := c.Request.Context()
	name := c.Param("BridgeName")
	btr := &bridges.BridgeTypeRequest{}

	taskType, err := bridges.ParseBridgeName(name)
	if err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	orm := btc.App.BridgeORM()
	bt, err := orm.FindBridge(ctx, taskType)
	if errors.Is(err, sql.ErrNoRows) {
		jsonAPIError(c, http.StatusNotFound, errors.New("bridge not found"))
		return
	}
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	if err := c.ShouldBindJSON(btr); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}
	if err := ValidateBridgeType(btr); err != nil {
		jsonAPIError(c, http.StatusBadRequest, err)
		return
	}
	if err := orm.UpdateBridgeType(ctx, &bt, btr); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	btc.App.GetAuditLogger().Audit(audit.BridgeUpdated, map[string]any{
		"bridgeName":                   bt.Name,
		"bridgeConfirmations":          bt.Confirmations,
		"bridgeMinimumContractPayment": bt.MinimumContractPayment,
		"bridgeURL":                    bt.URL,
	})

	jsonAPIResponse(c, presenters.NewBridgeResource(bt), "bridge")
}
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

**File:** core/web/schema/type/bridge.graphql (L1-10)
```text
type Bridge {
    id: ID!
    name: String!
    url: String!
    confirmations: Int!
    outgoingToken: String!
    minimumContractPayment: String!
    useConnectionManager: Boolean!
    createdAt: Time!
}
```

**File:** core/web/presenters/bridges_test.go (L39-57)
```go
	expected := `
{
	"data": {
		"type":"bridges",
		"id":"test",
		"attributes":{
			"name":"test",
			"url":"https://bridge.example.com/api",
			"confirmations":1,
			"outgoingToken":"vjNL7X8Ea6GFJoa6PBsvK2ECzNK3b8IZ",
			"minimumContractPayment":"1",
			"useConnectionManager":true,
			"createdAt":"2000-01-01T00:00:00Z"
		}
	}
}
`

	assert.JSONEq(t, expected, string(b))
```
