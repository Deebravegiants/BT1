This confirms the analog: `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` are accessible to `UserRoleView` (view-only role), per the routesRolesMap entries showing `viewOnlyAllowed: true` at [1](#0-0) , and the router wires them without any role restriction (unlike Create/Update/Destroy which use `auth.RequiresEditRole`) at [2](#0-1) . The `BridgeTypesController.Index`/`Show` handlers return `presenters.NewBridgeResource(bt)`, whose `OutgoingToken` field is always populated in plaintext, marshalled with no `omitempty`/redaction at [3](#0-2) . The GraphQL `bridge`/`bridges` queries expose the same `outgoingToken` field as non-null `String!` at [4](#0-3)  resolved directly from the DB value at [5](#0-4) .

### Title
Bridge OutgoingToken (external adapter credential) exposed in plain text to view-only users via `/v2/bridge_types` REST and GraphQL `bridge`/`bridges` queries - (File: core/web/presenters/bridges.go)

### Summary
The Chainlink node's Bridge (External Adapter) configuration exposes the `OutgoingToken` — a static credential the node uses to authenticate itself to the external adapter — in plain text on every read of bridge configuration, not just once at creation. This is reachable by any authenticated user holding the lowest-privilege `view` role, mirroring the Jenkins Aqua MicroScanner class of bug (CVE-2019-10427) where a configured secret was rendered in plain text in a configuration surface accessible beyond the intended privilege boundary.

### Finding Description
`BridgeType.OutgoingToken` is a long-lived secret used to authenticate outbound requests from the Chainlink node to the configured external adapter, stored in the DB at [6](#0-5) . The `BridgeResource` presenter, used by both `Index` and `Show` REST handlers, marshals `OutgoingToken` unconditionally (no `omitempty`, no redaction) as a required JSON field: [7](#0-6) .

The `Index` and `Show` handlers on `BridgeTypesController` build this resource directly from the ORM record and return it as-is: [8](#0-7) .

Critically, `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` are registered without any `auth.RequiresEditRole`/`RequiresAdminRole` wrapper, unlike `Create`, `Update`, and `Destroy` which are gated behind `auth.RequiresEditRole`: [2](#0-1) . The RBAC route map test explicitly documents that these GET routes are `viewOnlyAllowed: true`, i.e. reachable by the `view`-role: [1](#0-0) .

The same plaintext exposure exists in the GraphQL API: the `Bridge` type declares `outgoingToken: String!` non-null (no way to omit it), and both `BridgesPayload` (list) and `BridgePayload` (single) return it, resolved straight from the stored DB value: [9](#0-8) [5](#0-4) .

While the `IncomingToken` (the caller's credential) is intentionally shown only once at creation time via `omitempty` — a comment even says "The IncomingToken is only provided when creating a Bridge" — no equivalent restraint applies to `OutgoingToken`, which is instead treated as always-visible, non-sensitive metadata.

### Impact Explanation
Any user provisioned with the lowest privilege level (`UserRoleView`) intended for read-only dashboard access can retrieve the plaintext outgoing bridge credentials for every configured External Adapter by simply listing or viewing bridges. If that credential is reused for authorization at the external adapter (a common bridge design pattern), a view-only user gains the ability to directly query/interact with the external adapter under the node's identity, exceeding their intended read-only privilege — a direct secret-disclosure/privilege-boundary violation analogous to the Jenkins advisory's plaintext credential exposure in a configuration surface.

### Likelihood Explanation
High for any deployment that provisions `view`-role API tokens/sessions (a normal, supported, unprivileged tier per the RBAC design), since no additional preconditions, timing, or race conditions are required — a single authenticated GET request against `/v2/bridge_types`, `/v2/bridge_types/:BridgeName`, or the GraphQL `bridge`/`bridges` query is sufficient.

### Recommendation
Redact `OutgoingToken` from `BridgeResource` and the GraphQL `Bridge` type on read paths (`Index`/`Show`, `bridge`/`bridges` resolvers), following the same `omitempty`/one-time-disclosure pattern already used for `IncomingToken`. If the outgoing token must remain visible for operational reasons, restrict `GET /v2/bridge_types*` and the GraphQL bridge queries to `edit`/`admin` roles rather than `view`.

### Proof of Concept
1. Provision a user with `sessions.UserRoleView` (the lowest role) and authenticate a session/API token, as done in `TestRBAC_Routemap_ViewOnly` at [10](#0-9) .
2. Send `GET /v2/bridge_types` (or `GET /v2/bridge_types/<name>`) with that session — the route allows it per `viewOnlyAllowed: true` for these entries: [1](#0-0) .
3. Observe the JSON response includes `attributes.outgoingToken` in plain text for every bridge, as demonstrated by the presenter test fixture: [11](#0-10) .
4. Equivalently, issue the GraphQL query `{ bridges { results { outgoingToken } } }` as a view-role user; it succeeds and returns the plaintext token, per the schema and resolver: [4](#0-3) [5](#0-4) .

### Citations

**File:** core/web/auth/auth_test.go (L227-231)
```go
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
	{"DELETE", "/v2/bridge_types/MOCK", false, false, true},
```

**File:** core/web/auth/auth_test.go (L484-496)
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

**File:** core/web/schema/type/bridge.graphql (L1-19)
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

# BridgePayload defines the response to fetch a single bridge by name
union BridgePayload = Bridge | NotFoundError

# BridgesPayload defines the response when fetching a page of bridges
type BridgesPayload implements PaginatedPayload {
    results: [Bridge!]!
    metadata: PaginationMetadata!
}
```

**File:** core/web/resolver/bridge.go (L52-55)
```go
// OutgoingToken resolves the bridge's outgoing token.
func (r *BridgeResolver) OutgoingToken() string {
	return r.bridge.OutgoingToken
}
```

**File:** core/bridges/bridge_type.go (L57-67)
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
