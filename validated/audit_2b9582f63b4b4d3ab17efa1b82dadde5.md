### Title
Bridge OutgoingToken (external adapter credential) exposed unencrypted to view-role users via `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` - (File: core/web/presenters/bridges.go)

### Summary
Chainlink's `BridgeType` stores an `OutgoingToken` credential used to authenticate the node's outbound requests to an external adapter (bridge). This token is returned in plaintext by the bridge listing/detail JSON-API responses, which are explicitly allowed for the lowest-privileged `view` role. This mirrors CVE-2019-10385's bug class: a credential intended to be a secret is stored/served such that a low-privileged, unprivileged-relative-to-secret-management user can read it.

### Finding Description
`BridgeType.OutgoingToken` is a credential the Chainlink node uses to authenticate itself to the external adapter when calling out [1](#0-0) . `presenters.NewBridgeResource` copies this token verbatim into the JSON-API resource with no `omitempty` or redaction, unlike `IncomingToken`, which is only attached in the create flow and marked `omitempty` [2](#0-1) . The `Index` and `Show` handlers of `BridgeTypesController` build this resource directly from the DB record and return it as-is for `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` [3](#0-2) . The RBAC test matrix confirms these two GET routes are `viewOnlyAllowed: true`, i.e., reachable by the lowest privilege API role (`view`) [4](#0-3) , and `TestRBAC_Routemap_ViewOnly` asserts such routes must not return 401/403 for a `view`-role user [5](#0-4) . The GraphQL schema exposes the same field unconditionally as a non-nullable `outgoingToken: String!` on the `Bridge` type for both single and paginated bridge queries [6](#0-5) , and the resolver returns it directly from the DB model without redaction [7](#0-6) .

### Impact Explanation
A user granted the minimal `view` role (intended only for read-only monitoring, per `chainlink admin users create --role view`) can retrieve the `OutgoingToken` for any configured bridge via a simple authenticated GET request or GraphQL query. This token authenticates the node to the external adapter; disclosure lets the low-privileged user impersonate the node to that adapter or otherwise misuse the credential outside the node's control — directly analogous to the Jenkins eggPlant plugin CVE where users with only "Extended Read" could recover credentials meant to be secret.

### Likelihood Explanation
High: no special conditions are needed. Any account provisioned with the `view` role (the lowest, most commonly delegated role for read-only dashboards/monitoring) can call `GET /v2/bridge_types` or the `bridges`/`bridge` GraphQL query and receive the token in the response body, as validated by the existing RBAC and resolver tests themselves.

### Recommendation
Redact `OutgoingToken` from `BridgeResource` and the GraphQL `Bridge` type for read/list operations, exposing it only at credential-issuance time (analogous to how `IncomingToken` is `omitempty` and only set on create), or require `edit`/`admin` role to view bridge tokens.

### Proof of Concept
1. Create an admin/edit user and a bridge with `POST /v2/bridge_types` (captures `outgoingToken`).
2. Create a second user with role `view` (`chainlink admin users create --email view@x.com --role view`).
3. Authenticate as the `view` user and call `GET /v2/bridge_types/<bridgeName>` (or the GraphQL `bridge(id: "<name>")` query with field `outgoingToken`).
4. Observe the response includes `"outgoingToken": "<the-secret-token>"` in plaintext, confirming credential disclosure to a read-only-privileged actor.

### Citations

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

**File:** core/web/auth/auth_test.go (L227-230)
```go
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
```

**File:** core/web/auth/auth_test.go (L484-531)
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
