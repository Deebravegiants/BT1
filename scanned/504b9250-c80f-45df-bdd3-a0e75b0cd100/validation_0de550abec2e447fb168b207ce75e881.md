### Title
Bridge `OutgoingToken` credential disclosed to any authenticated user regardless of role via `GET /v2/bridge_types` - (File: core/web/router.go)

### Summary
The Chainlink node exposes the plaintext `OutgoingToken` for every configured Bridge to *any* authenticated user, including the lowest-privilege `View`/`Read` role, because the read routes for bridge types carry no role-based middleware while all mutating routes on the same resource are explicitly gated with `RequiresEditRole`/`RequiresAdminRole`. This is the same bug class as the MobSF advisory: a functionality intended to be privilege-scoped instead returns a full-access credential to a low-privileged, authenticated caller.

### Finding Description
`v2Routes` in `core/web/router.go` registers the bridge type endpoints as: [1](#0-0) 

`GET /bridge_types` (`Index`) and `GET /bridge_types/:BridgeName` (`Show`) have no `auth.RequiresEditRole`/`auth.RequiresAdminRole` wrapper — only session/token authentication is required — while `POST`, `PATCH`, and `DELETE` on the same resource are correctly wrapped with `auth.RequiresEditRole`.

Both `Index` and `Show` return a `presenters.BridgeResource`, which unconditionally serializes `OutgoingToken`: [2](#0-1) [3](#0-2) [4](#0-3) 

`OutgoingToken` is a real secret generated at bridge creation time (`utils.NewSecret(24)`) and stored in plaintext in the `bridge_types` table, used by the node to authenticate its outbound requests to the external adapter: [5](#0-4) 

Because the role check `RequiresEditRole`/`RequiresAdminRole` (defined in `core/web/auth/auth.go`) is the only mechanism separating a `View`-role user from an `Edit`/`Admin`-role user, and that check is simply absent from the `GET` routes, a user provisioned with only `View` access (the intended minimal, read-only role) can call `GET /v2/bridge_types` or `GET /v2/bridge_types/:BridgeName` and receive the same `OutgoingToken` secret that an `Admin` would see — a functionality that is "not efficient" in exactly the way described in the MobSF report, where any low-privilege authenticated user can retrieve a privileged secret through a legitimate, unprivileged-role-reachable endpoint.

### Impact Explanation
`OutgoingToken` authenticates the Chainlink node to the configured external adapter/bridge endpoint. Disclosure of this token to a low-privilege user (who was only meant to have read-only visibility into job/bridge configuration, not secrets) allows that user to impersonate the node when calling the external adapter, or to reuse/leak the credential outside the node's trust boundary — a concrete instance of unauthorized secret disclosure/role bypass, matching the "Accept only concrete... key/secret disclosure" criterion.

### Likelihood Explanation
High. No special conditions are needed beyond having any valid, low-privilege (`View`) authenticated session or API token — which is the intended minimal access level for a "read-only" operator-provisioned account. `Index`/`Show` are simple `GET` requests requiring no elevated role, no CSRF token, and no additional confirmation (unlike `NewAPIToken`, which correctly re-verifies the password). This mirrors the external report precisely: a "registered user" (any authenticated node user) can, through a normal read/browsing feature, retrieve a secret meant to be protected at a higher privilege tier.

### Recommendation
Wrap `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` with the same role gate used for the corresponding write operations (at minimum `auth.RequiresEditRole`, consistent with how `keys/*` export endpoints are `RequiresAdminRole`-gated). Alternatively, omit `OutgoingToken` from the `BridgeResource` presenter for read/list responses (as is already done for `IncomingToken`, which is `omitempty` and only populated on `Create`), returning it only at bridge-creation time.

### Proof of Concept
1. As an Admin, create a bridge: `POST /v2/bridge_types` with `{"name":"test-bridge","url":"https://adapter.example.com"}` — this generates and stores an `OutgoingToken`.
2. Create/authenticate as a `View`-role user (the minimal privilege role) via a session cookie or API token created with `View` role.
3. As that `View`-role user, call `GET /v2/bridge_types/test-bridge` (or `GET /v2/bridge_types`).
4. Observe the JSON response includes `"outgoingToken": "<plaintext secret>"` in `attributes`, identical to what an Admin would see — despite the route requiring no `RequiresEditRole`/`RequiresAdminRole` check, unlike all other bridge-mutation routes.

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

**File:** core/bridges/bridge_type.go (L55-102)
```go
// BridgeType is used for external adapters and has fields for
// the name of the adapter and its URL.
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

// NewBridgeType returns a bridge type authentication (with plaintext
// password) and a bridge type (with hashed password, for persisting)
func NewBridgeType(btr *BridgeTypeRequest) (*BridgeTypeAuthentication,
	*BridgeType, error,
) {
	incomingToken := utils.NewSecret(24)
	outgoingToken := utils.NewSecret(24)
	salt := utils.NewSecret(24)

	hash, err := incomingTokenHash(incomingToken, salt)
	if err != nil {
		return nil, nil, err
	}

	return &BridgeTypeAuthentication{
		Name:                   btr.Name,
		URL:                    btr.URL,
		Confirmations:          btr.Confirmations,
		IncomingToken:          incomingToken,
		OutgoingToken:          outgoingToken,
		MinimumContractPayment: btr.MinimumContractPayment,
		UseConnectionManager:   btr.UseConnectionManager,
	}, &BridgeType{
		Name:                   btr.Name,
		URL:                    btr.URL,
		Confirmations:          btr.Confirmations,
		IncomingTokenHash:      hash,
		Salt:                   salt,
		OutgoingToken:          outgoingToken,
		MinimumContractPayment: btr.MinimumContractPayment,
		UseConnectionManager:   btr.UseConnectionManager,
	}, nil
}
```
