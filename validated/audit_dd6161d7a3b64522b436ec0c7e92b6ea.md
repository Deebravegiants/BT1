## Finding

### Title
Bridge `OutgoingToken` secret is returned unmasked to any authenticated "view"-role user via the Bridge Types API - ([File: core/web/presenters/bridges.go])

### Summary
Chainlink's Bridge Types API (`GET /v2/bridge_types` and `GET /v2/bridge_types/:name`) returns the bridge's `OutgoingToken` field in plaintext in every response, with no role restriction beyond basic authentication and no field redaction (`omitempty` is applied only to `IncomingToken`, not `OutgoingToken`).

### Finding Description
`BridgeResource` in `core/web/presenters/bridges.go` defines `OutgoingToken` without `omitempty`, and `NewBridgeResource` unconditionally copies `b.OutgoingToken` from the persisted `bridges.BridgeType` model into the JSON representation: [1](#0-0) 

`BridgeTypesController.Index` and `.Show` both build responses via `presenters.NewBridgeResource(bridge)` with no field stripping based on caller role: [2](#0-1) 

The comment `// The IncomingToken is only provided when creating a Bridge` at line 16 shows the developers were aware that some bridge secret material should be write-only/one-time-disclosure — this discipline was applied to `IncomingToken` (via `omitempty`, only populated in `Create`) but was not applied to `OutgoingToken`, which is always serialized on every subsequent `Index`/`Show` call.

Role-based access to the Web API only requires "view" role for GET routes (`authenticateUser`/view-only checks in `core/web/auth/auth.go`, exercised by `TestRBAC_Routemap_ViewOnly`), so any minimally-privileged, authenticated node operator user — not just admins — can retrieve this token by listing or reading bridges: [3](#0-2) 

This mirrors the Jenkins ByteGuard CWE-311 pattern: a credential/token that should be treated as a secret is persisted and served back unmasked to users who only need read access, rather than being redacted or write-only.

### Impact Explanation
`OutgoingToken` is a bridge authentication credential. Disclosure to any authenticated low-privilege ("view") user allows that user to impersonate the node/bridge relationship or use the token against the external adapter/bridge endpoint, potentially enabling unauthorized calls to the bridge on the node's behalf. This is a confidentiality-only, no-integrity-impact issue (matches the CVSS profile of the source advisory: C:L/I:N/A:N), since the leak itself doesn't directly let the caller move funds or bypass job/run authorization, but it does expose an authentication secret beyond its intended trust boundary.

### Likelihood Explanation
Any authenticated user with the lowest privilege role (`view`) can trivially trigger this by calling `GET /v2/bridge_types` or `GET /v2/bridge_types/:BridgeName` — no special permissions, timing, or race conditions required. This is a straightforward direct read of an already-reachable API endpoint.

### Recommendation
Apply the same write-only/one-time-disclosure treatment to `OutgoingToken` as is done for `IncomingToken`: only populate `OutgoingToken` in the `Create` response, mark the JSON field with `omitempty`, and return an empty/redacted value from `Index`/`Show`/`Update`. Consider also gating retrieval of both tokens behind an `admin`/`edit` role rather than `view`.

### Proof of Concept
1. Create an authenticated session/API token for a user with role `view`.
2. Have an admin create a bridge (`POST /v2/bridge_types`) — this generates and stores an `OutgoingToken`.
3. As the `view`-role user, call `GET /v2/bridge_types/:BridgeName` (or `GET /v2/bridge_types` to list all).
4. Observe the response JSON contains the bridge's `outgoingToken` field in plaintext, confirmed by `NewBridgeResource` always setting `OutgoingToken: b.OutgoingToken` with no redaction and no `omitempty` tag: [4](#0-3)

### Citations

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

**File:** core/web/auth/auth_test.go (L484-532)
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
}
```
