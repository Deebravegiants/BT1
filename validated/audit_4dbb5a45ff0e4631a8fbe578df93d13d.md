### Title
Bridge secret `OutgoingToken` disclosed to low-privileged (view-only) authenticated users - (File: `core/web/router.go`)

### Summary
The `GET /v2/bridge_types/:BridgeName` endpoint is reachable by any authenticated user regardless of role, including `UserRoleView` (the lowest-privilege role), and returns the bridge's `OutgoingToken` secret in the response body. This mirrors the CVE-2021-42568 bug class: a sensitive, credential-adjacent function is reachable by a low-privileged account because the intended access-control gate was not applied to a specific action while it was applied to sibling actions on the same resource.

### Finding Description
In `core/web/router.go`, the bridge-types routes are registered as: [1](#0-0) 

`Create`, `Update`, and `Destroy` are explicitly wrapped with `auth.RequiresEditRole`, but `Show` (the `GET /v2/bridge_types/:BridgeName` handler) is registered with no role wrapper at all — it only passes through the generic `Authenticate` middleware (session or API token), so any valid user session (View, Run, Edit, Admin) can call it. This is corroborated by the RBAC route map test table, which explicitly marks this route as accessible to view-only users: [2](#0-1) 

The `Show` handler itself does no additional per-field authorization and serializes the full bridge record via `presenters.NewBridgeResource`: [3](#0-2) 

The presenter includes `OutgoingToken` unconditionally in the JSON response (unlike `IncomingToken`, which is `omitempty` and only populated at creation time): [4](#0-3) 

The stored `BridgeType.OutgoingToken` is a 24-byte random secret generated at bridge creation, alongside `IncomingTokenHash`/`Salt` used to authenticate inbound bridge calls: [5](#0-4) 

Because `OutgoingToken` is stored and returned in plaintext (not hashed like the incoming token), and the `Show` route has no elevated role requirement, a low-privileged `View` role user (who is only supposed to have read access to non-sensitive resources) can retrieve this credential for any configured bridge by name.

### Impact Explanation
`OutgoingToken` is a bridge-specific secret intended to let the external adapter/bridge validate that a request genuinely originated from the Chainlink node (an authentication credential for outbound bridge calls). Disclosure of this token to a low-privileged, view-only account allows that account to obtain a secret it is not supposed to have access to, potentially enabling impersonation of the node to the external bridge/adapter or forging bridge-authenticated traffic, depending on how the specific external adapter is configured to validate this token. This matches the "key/secret disclosure" and "cross-role privilege confusion" impact categories called out in scope.

### Likelihood Explanation
Likelihood is high for any deployment where operators create low-privilege (`View`) accounts for read-only dashboards/monitoring, since no special conditions are required — a simple authenticated `GET /v2/bridge_types/:BridgeName` call, or the equivalent GraphQL `bridge` query (which also exposes `outgoingToken` to any authenticated session per the schema and resolver test), is sufficient: [6](#0-5) [7](#0-6) 

### Recommendation
- Restrict `GET /v2/bridge_types/:BridgeName` (and the GraphQL `bridge`/`bridges` resolvers) to require at least `Edit` (or a role consistent with the sensitivity of `OutgoingToken`), matching the role requirement already applied to `Create`/`Update`/`Destroy`.
- Alternatively, redact `OutgoingToken` from the `Show`/`Index` responses for non-privileged roles, following the same `omitempty`/creation-only pattern already used for `IncomingToken`.
- Audit other read-only (`GET`) routes in `core/web/router.go` for the same pattern (endpoint has no role wrapper while sibling write endpoints do) to ensure no other secrets leak through under-restricted `Show`/`Index` actions.

### Proof of Concept
1. Create a `View`-role user/API token on a running Chainlink node (`RequiresEditRole`/`RequiresAdminRole` not required to create view users by an admin, but any existing view-role session works).
2. As the view-role user, call `GET /v2/bridge_types/<bridgeName>` for an existing bridge.
3. Observe the JSON response includes `"outgoingToken": "<secret>"` even though the calling user only has `View` role — confirmed by the test asserting this route is `viewOnlyAllowed: true` in the RBAC matrix (`core/web/auth/auth_test.go:229`) and by the presenter always serializing `OutgoingToken` (`core/web/presenters/bridges.go:18`).

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

**File:** core/web/auth/auth_test.go (L227-231)
```go
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
	{"DELETE", "/v2/bridge_types/MOCK", false, false, true},
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

**File:** core/web/resolver/bridge_test.go (L86-129)
```go
func Test_Bridge(t *testing.T) {
	t.Parallel()

	var (
		query = `
			query GetBridge{
				bridge(id: "bridge1") {
					... on Bridge {
						id
						name
						url
						confirmations
						outgoingToken
						minimumContractPayment
						createdAt
					}
					... on NotFoundError {
						message
						code
					}
				}
			}`

		name = bridges.BridgeName("bridge1")
	)
	bridgeURL, err := url.Parse("https://external.adapter")
	require.NoError(t, err)

	testCases := []GQLTestCase{
		unauthorizedTestCase(GQLTestCase{query: query}, "bridge"),
		{
			name:          "success",
			authenticated: true,
			before: func(ctx context.Context, f *gqlTestFramework) {
				f.App.On("BridgeORM").Return(f.Mocks.bridgeORM)
				f.Mocks.bridgeORM.On("FindBridge", mock.Anything, name).Return(bridges.BridgeType{
					Name:                   name,
					URL:                    models.WebURL(*bridgeURL),
					Confirmations:          uint32(1),
					OutgoingToken:          "outgoingToken",
					MinimumContractPayment: assets.NewLinkFromJuels(1),
					CreatedAt:              f.Timestamp(),
				}, nil)
			},
```

**File:** deployment/environment/web/sdk/internal/schema.graphql (L121-126)
```text
    url: String!
    confirmations: Int!
    outgoingToken: String!
    minimumContractPayment: String!
    createdAt: Time!
}
```
