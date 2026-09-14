### Title
Bridge `OutgoingToken` credential exposed in plaintext to view-only role via `GET /v2/bridge_types/:BridgeName` - (File: core/web/presenters/bridges.go)

### Summary
Chainlink stores the bridge's `OutgoingToken` — a credential used to authenticate outbound requests to an external adapter — and returns it unredacted in the JSON API response for `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName`. These read endpoints are accessible to the lowest-privilege authenticated role (`view`), analogous to the Jenkins FitNesse CVE where users with only "Extended Read" permission could view plaintext credentials stored in job configs.

### Finding Description
`BridgeType.OutgoingToken` is stored in plaintext in the database (unlike `IncomingToken`, which is only ever hashed via `IncomingTokenHash`) [1](#0-0) . When bridges are listed or fetched, `presenters.NewBridgeResource` copies `OutgoingToken` directly into the JSON API resource with no redaction and no `omitempty`/masking, unlike `IncomingToken` which is only populated on creation [2](#0-1) .

The controller's `Index` and `Show` handlers serialize this resource directly for any authenticated request: `Index` returns paginated bridges via `NewBridgeResource`, and `Show` returns a single bridge, both including the raw `OutgoingToken` [3](#0-2) .

Per the RBAC test matrix, `GET /v2/bridge_types` and `GET /v2/bridge_types/MOCK` are both marked `viewOnlyAllowed: true`, meaning a user created with the `view` role (the lowest privilege, read-only role) is authorized to call these routes without receiving `401`/`403` [4](#0-3) [5](#0-4) . This is confirmed by the general chainlink pattern of secret redaction elsewhere in the codebase (e.g. `models.Secret`/`SecretURL` types that redact as `"xxxxx"` when marshaled) [6](#0-5) , showing the project's own security expectation that credential-bearing fields must be redacted — an expectation the `OutgoingToken` field violates for the `view` role.

### Impact Explanation
The `OutgoingToken` is used by external adapters to authenticate that a request truly originated from the Chainlink node (it is embedded in the metadata payload sent to bridges) [7](#0-6) . A `view`-role user — who is meant to have read-only, non-privileged access to node state — can retrieve this secret and use it to impersonate the Chainlink node when calling the configured external adapter, or to correlate/tamper with responses expected by that adapter. This is a credential-disclosure issue enabling request impersonation against externally-facing bridge integrations, matching the class of the Jenkins CVE (secret readable by a lower-privileged actor than intended).

### Likelihood Explanation
Any operator who provisions a `view`-role API user (a common, intentionally low-trust role for dashboards/monitoring per `chainlink admin users create --role=view`) can trivially call `GET /v2/bridge_types` or `GET /v2/bridge_types/:BridgeName` to retrieve the token — no additional exploitation steps or privilege escalation required.

### Recommendation
Redact `OutgoingToken` in `presenters.NewBridgeResource` for `Index`/`Show` responses to `view` and `run` roles (only return it on creation/update via `edit`/`admin`, mirroring how `IncomingToken` is handled), or wrap it in the same `models.Secret` redaction type used elsewhere in the codebase before serialization.

### Proof of Concept
1. Provision a user with `view` role: `chainlink admin users create --email=viewer@example.com --role=view`.
2. Log in as that user and call `GET /v2/bridge_types/<bridge-name>` (or `GET /v2/bridge_types` for the full list).
3. Observe the JSON API response includes `"outgoingToken": "<plaintext-token>"` in `attributes`, confirmed by the existing test fixture showing the unredacted field [8](#0-7) .
4. Use the retrieved token to send crafted requests to the bridge's configured external adapter, impersonating the node.

Note: I was unable to fully trace the exact router registration lines for `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` in `core/web/router.go` (the grep for that specific block did not return the surrounding route-setup code), so the RBAC middleware wrapping (or absence thereof) on these two specific routes is inferred from the `routesRolesMap` test table rather than directly read from the router source. This should be verified directly in `core/web/router.go` before treating this as fully confirmed.

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

**File:** core/store/models/secrets.go (L7-12)
```go
// Secret is a string that formats and encodes redacted, as "xxxxx".
// Deprecated
type Secret = config.SecretString

// Deprecated
func NewSecret(s string) *Secret { return config.NewSecretString(s) }
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
