## Finding

### Title
View-role users can read bridge `outgoingToken` secrets via `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` - (File: core/web/presenters/bridges.go)

### Summary
Chainlink's Bridge Types API exposes the `outgoingToken` credential (used by the node to authenticate itself when calling external bridge/adapter URLs) in plaintext to any authenticated user, including the lowest-privileged `view` role. This mirrors the CVE-2022-25184 bug class: a secret value that should be restricted to privileged users is returned to a user who only has read access.

### Finding Description
The `BridgeTypesController.Index` and `.Show` handlers serialize bridge records through `presenters.NewBridgeResource`, whose `OutgoingToken` field is tagged `json:"outgoingToken"` (no `omitempty`, no redaction), unlike the `IncomingToken` field which is explicitly marked `omitempty` and only populated on creation. [1](#0-0) [2](#0-1) 

The routes `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` are registered without any `RequiresEditRole`/`RequiresAdminRole` wrapper — only mutating verbs (`POST`, `PATCH`, `DELETE`) are gated: [3](#0-2) 

This is confirmed by the RBAC test matrix, which explicitly marks both GET routes as `viewOnlyAllowed: true`: [4](#0-3) 

The `Show`/`Index` controller code performs no field-level filtering by role before calling `presenters.NewBridgeResource(bt)`: [5](#0-4) 

### Impact Explanation
`OutgoingToken` is a live secret credential — it is the value the node itself uses to authenticate outbound calls to the configured bridge/external adapter URL, generated via `utils.NewSecret(24)` at bridge creation time and persisted unhashed in the `BridgeType.OutgoingToken` field. [6](#0-5) 
An unprivileged `view`-role user (the lowest role in the RBAC hierarchy, intended only for dashboards/monitoring) can retrieve this token for every configured bridge via a simple authenticated `GET`, without needing edit/admin permissions. This is a real secret disclosure to a lower-privileged principal, analogous to how the Jenkins plugin leaked password defaults to `Item/Read`-only users.

### Likelihood Explanation
Any authenticated user with `view` role — the least privileged non-anonymous role in Chainlink's node UI — can trigger this with a single unauthenticated-role-check `GET` request; no special conditions are required.

### Recommendation
Restrict `outgoingToken` visibility in `BridgeResource` to users with at least `edit`/`admin` role (e.g., strip/redact the field for `view`-role sessions in `BridgeTypesController.Index`/`Show`, similar to how `IncomingToken` is only populated on create), or gate `GET /v2/bridge_types*` behind `auth.RequiresEditRole`.

### Proof of Concept
1. Create a bridge as an admin/edit user (`POST /v2/bridge_types`), noting the returned `outgoingToken`.
2. Authenticate as a user with `UserRoleView`.
3. Call `GET /v2/bridge_types/<BridgeName>` or `GET /v2/bridge_types`.
4. Observe the response JSON includes the plaintext `outgoingToken` field, confirmed by the presenter test fixture showing `outgoingToken` always serialized: [7](#0-6) 

---

Note: this reflects existing, seemingly intentional API design (the RBAC test explicitly asserts view-role access is allowed), so this may be a known/accepted design tradeoff rather than an unreviewed bug — worth confirming with the Chainlink security team whether `outgoingToken` is treated as sensitive or as a semi-public identifier.

### Citations

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

**File:** core/web/router.go (L268-273)
```go
		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
```

**File:** core/web/auth/auth_test.go (L227-231)
```go
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
	{"DELETE", "/v2/bridge_types/MOCK", false, false, true},
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

**File:** core/bridges/bridge_type.go (L63-76)
```go
	OutgoingToken          string        `db:"outgoing_token"`
	MinimumContractPayment *assets.Link  `db:"minimum_contract_payment"`
	CreatedAt              time.Time     `db:"created_at"`
	UpdatedAt              time.Time     `db:"updated_at"`
	UseConnectionManager   bool          `db:"use_connection_manager" json:"useConnectionManager"`
}

// NewBridgeType returns a bridge type authentication (with plaintext
// password) and a bridge type (with hashed password, for persisting)
func NewBridgeType(btr *BridgeTypeRequest) (*BridgeTypeAuthentication,
	*BridgeType, error,
) {
	incomingToken := utils.NewSecret(24)
	outgoingToken := utils.NewSecret(24)
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
