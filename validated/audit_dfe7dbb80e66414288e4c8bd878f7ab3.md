Audit Report

## Title
Bridge `OutgoingToken` credential exposed in plaintext to view-only role via `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` - (File: core/web/presenters/bridges.go)

## Summary
`core/bridges/bridge_type.go` stores `OutgoingToken` in plaintext (unlike `IncomingTokenHash`, which is hashed) [1](#0-0) , and `presenters.NewBridgeResource` unconditionally copies this field into the JSON API response with no redaction or `omitempty` tag, unlike `IncomingToken` which is deliberately restricted to creation-time responses [2](#0-1) . The `Index` and `Show` handlers in `bridge_types_controller.go` serialize this resource for any authenticated caller, including users with only the `view` role [3](#0-2) .

## Finding Description
`NewBridgeResource` sets `OutgoingToken: b.OutgoingToken` directly from the DB-stored plaintext value with no masking logic, while `IncomingToken` is only ever populated separately in the `Create` handler (`resource.IncomingToken = bta.IncomingToken`) and defaults to empty (dropped by `omitempty`) everywhere else [4](#0-3) [5](#0-4) . `Index` and `Show` both call `presenters.NewBridgeResource` and return it directly with no field stripping based on caller role [6](#0-5) [7](#0-6) . This is corroborated by the presenter's own test fixture, which shows `outgoingToken` unredacted in serialized output [8](#0-7) .

The RBAC test suite explicitly marks `GET /v2/bridge_types` and `GET /v2/bridge_types/MOCK` as `viewOnlyAllowed: true` [9](#0-8) , and `TestRBAC_Routemap_ViewOnly` runs a `view`-role user against every route in this table, asserting a non-401/403 response for `viewOnlyAllowed` routes [10](#0-9) . This confirms that a `view`-role authenticated session is permitted to hit these two read endpoints and receive the full bridge resource, including the plaintext `OutgoingToken`, with no redaction path anywhere in the presenter or controller code.

## Impact Explanation
`OutgoingToken` is used to authenticate outbound requests to external adapters. Its unredacted exposure to the lowest-privilege authenticated role (`view`) allows a low-trust API user (e.g., a monitoring/dashboard account) to extract a credential intended for node-to-adapter authentication and use it to impersonate the node or interfere with adapter integrations. This is a legitimate secret-disclosure / least-privilege violation reachable purely via authenticated, unprivileged (`view`-role) API calls — it does not require any admin/operator access, database access, or leaked credentials from elsewhere; the credential disclosure itself is the vulnerability.

## Likelihood Explanation
Any operator who creates a `view`-role API user (a standard, documented low-trust role) exposes this token to that user by design of the current code — no exploitation steps beyond a normal authenticated `GET` request are needed. This is trivially and repeatably reachable.

## Recommendation
Redact `OutgoingToken` from `presenters.NewBridgeResource` for `Index`/`Show` responses served to `view` (and arguably `run`) roles — only return it at creation/update time to `edit`/`admin` roles, mirroring the `IncomingToken` handling, or wrap it using the existing `models.Secret`/`config.SecretString` redaction type used elsewhere in the codebase.

## Proof of Concept
1. Create a `view`-role user (`chainlink admin users create --role=view`).
2. Log in as that user and issue `GET /v2/bridge_types/<bridge-name>` or `GET /v2/bridge_types`.
3. Confirm via `TestRBAC_Routemap_ViewOnly`-style test that the response is not 401/403 [11](#0-10) , and inspect the JSON body's `attributes.outgoingToken` field, which contains the plaintext token as shown in the presenter test fixture [8](#0-7) .
4. Use the extracted token against the bridge's configured external adapter to demonstrate impersonation capability.

### Citations

**File:** core/bridges/bridge_type.go (L55-68)
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

**File:** core/web/presenters/bridges_test.go (L39-54)
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
