### Title
Bridge outgoing token plaintext disclosure to view-only authenticated users - ([File: core/web/bridge_types_controller.go])

### Summary
Similar to the Jenkins Report Portal issue (CVE-2023-30523), where low-privilege users (Item/Extended Read) could read unencrypted tokens through the plugin's stored configuration, Chainlink's `BridgeType.OutgoingToken` is stored in plaintext in the database [1](#0-0)  and is returned unredacted to any authenticated user with the lowest ('view') role via `GET /v2/bridge_types/:BridgeName`.

### Finding Description
`BridgeTypesController.Show` fetches the bridge and serializes it with `presenters.NewBridgeResource`, which unconditionally copies `OutgoingToken` into the JSON response with no redaction [2](#0-1) [3](#0-2) .

The router explicitly allows this endpoint for `viewOnlyAllowed` users, i.e., the lowest-privileged authenticated role, alongside edit/admin: `{"GET", "/v2/bridge_types/MOCK", true, true, true}` and the route wiring `authv2.GET("/bridge_types/:BridgeName", bt.Show)` has no role-gating middleware (unlike Create/Update/Destroy, which use `auth.RequiresEditRole`) [4](#0-3) [5](#0-4) .

The GraphQL bridge resolver behaves the same way — `OutgoingToken()` is exposed and only requires generic `authenticateUser` (view-level session), not `authenticateUserCanEdit`/Admin [6](#0-5) [7](#0-6) .

The `OutgoingToken` is a genuine secret: it's the credential the Chainlink node presents to the external bridge/adapter when making outbound calls (`BridgeTypeAuthentication.OutgoingToken`, generated via `utils.NewSecret(24)`) [8](#0-7) . Unlike `IncomingTokenHash`, which is properly hashed with a salt and never exposed after creation, `OutgoingToken` is stored and returned in plaintext by design for the `Show`/`Index`/`Update`/`Destroy` responses.

### Impact Explanation
A user granted only the 'view' role (the lowest role in Chainlink's RBAC — intended for read-only dashboards/monitoring per `RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole` gating elsewhere) can retrieve a live outgoing authentication token for any configured bridge/external adapter. This mirrors the Jenkins analog exactly: unprivileged/limited-permission actors gain disclosure of a secret credential meant to be restricted to higher-privileged operators, enabling impersonation of the node to that external adapter or reuse of the token elsewhere.

### Likelihood Explanation
High. This requires only a valid session/API token with the default lowest ('view') role and a single unauthenticated-parameter GET request (`GET /v2/bridge_types/:BridgeName`) — no exploitation complexity, race condition, or special access needed, matching the "unprivileged-actor" scope of this analog.

### Recommendation
Restrict read access to `OutgoingToken` (and the equivalent GraphQL field) to `edit`/`admin` roles only, or omit/redact the token from `Show`/`Index`/GraphQL responses entirely and instead expose a rotation-only mechanism, consistent with how `IncomingToken` is only ever surfaced once at creation time (`resource.IncomingToken = bta.IncomingToken` in `Create`) [9](#0-8) .

### Proof of Concept
1. Create an API user with role `view` (`clsession.UserRoleView`).
2. Authenticate and call `GET /v2/bridge_types/<bridgeName>`.
3. Observe the JSON response includes `"outgoingToken": "<plaintext secret>"`, as confirmed by the RBAC test asserting this route is `viewOnlyAllowed` and by the presenter always populating `OutgoingToken` [10](#0-9) [11](#0-10) .

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

**File:** core/bridges/bridge_type.go (L70-102)
```go
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

**File:** core/web/bridge_types_controller.go (L98-99)
```go
	resource := presenters.NewBridgeResource(*bt)
	resource.IncomingToken = bta.IncomingToken
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

**File:** core/web/presenters/bridges.go (L29-42)
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
}
```

**File:** core/web/auth/auth_test.go (L227-230)
```go
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
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

**File:** core/web/resolver/bridge.go (L52-55)
```go
// OutgoingToken resolves the bridge's outgoing token.
func (r *BridgeResolver) OutgoingToken() string {
	return r.bridge.OutgoingToken
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
