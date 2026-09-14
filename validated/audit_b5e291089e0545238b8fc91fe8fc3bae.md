Based on the analog scan, I found a concrete valid analog for the Keycloak secret-disclosure bug class in this codebase.

### Title
Bridge outgoing token secret disclosed in plaintext to view-only users via bridge endpoints - ([File: core/web/presenters/bridges.go])

### Summary
The Keycloak advisory describes a config endpoint returning unmasked reCAPTCHA secrets to view-only administrators. Chainlink's bridge subsystem has the same bug class: the `OutgoingToken` credential used to authenticate the node's outgoing calls to an external adapter is stored and returned in plaintext by every bridge-reading path, including endpoints and GraphQL queries that are explicitly allowed for `UserRoleView` (view-only) sessions.

### Finding Description
`BridgeType.OutgoingToken` is stored in cleartext in the DB (unlike `IncomingTokenHash`, which is hashed) and is copied verbatim into `BridgeResource.OutgoingToken` by `NewBridgeResource`: [1](#0-0) [2](#0-1) 

Both `BridgeTypesController.Index` (list all bridges) and `BridgeTypesController.Show` (get one bridge) build this resource directly from the ORM record with no redaction of `OutgoingToken`: [3](#0-2) 

The RBAC test matrix confirms `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` are explicitly `viewOnlyAllowed: true`: [4](#0-3) 

And the view-only role test asserts these routes must NOT return `401`/`403` for a `sessions.UserRoleView` user: [5](#0-4) 

The same field is also exposed unredacted through the GraphQL `bridge`/`bridges` resolvers (`BridgeResolver.OutgoingToken`): [6](#0-5) 

This is functionally identical to the Keycloak bug class: a secret used to authenticate with a third-party/external service (there: reCAPTCHA secret key; here: the bridge's `OutgoingToken` used to authenticate outbound webhook calls to the external adapter) is returned unmasked to a principal that only has read/view privileges.

### Impact Explanation
A user granted only the view-only role — intended for dashboards/monitoring and explicitly permitted read access to bridge configuration — can retrieve the plaintext `OutgoingToken` for every configured bridge. If this token is used by the external adapter to authenticate/validate that a callback truly originated from the Chainlink node (a common bridge pattern), a view-only user (or anyone who compromises a view-only session/API token) can extract it and impersonate the node when calling the external adapter, or otherwise misuse the credential outside the node. This is a credential-disclosure issue reachable by an unprivileged (relative to admin/edit) authenticated actor.

### Likelihood Explanation
Likelihood is high for any deployment using the view-only role (a documented, intended RBAC tier) or LDAP/OIDC read-only group mappings (`ReadUserGroupCN`/`ReadClaim`) that map external directory groups to this role: [7](#0-6) 
No special conditions are required beyond having any valid view-only session/API token and knowing (or enumerating via `Index`) a bridge name — both explicitly supported, tested code paths.

### Recommendation
Redact `OutgoingToken` (and any other bridge secret) from `BridgeResource`/`BridgeResolver` responses for `Show`/`Index`/GraphQL `bridge`/`bridges` queries, or restrict its visibility to `UserRoleAdmin`/`UserRoleEdit` (consistent with how `IncomingToken` is already only returned once, at creation time, via `Create`). Alternatively, mask the value (e.g., render as `"xxxxx"`, matching the pattern already used for `Secret`/`SecretURL` config redaction) unless the requester has edit/admin role.

### Proof of Concept
1. Create a bridge as an admin: `POST /v2/bridge_types` with body `{"name":"mybridge","url":"https://adapter.example.com"}` — response includes plaintext `outgoingToken`.
2. Create/authenticate a session for a user with `Role: sessions.UserRoleView`.
3. As that view-only user, call `GET /v2/bridge_types/mybridge` (or `GET /v2/bridge_types` to list all).
4. Observe the JSON response contains `"outgoingToken": "<plaintext value>"`, confirming the view-only user can read the bridge's outgoing authentication secret — as shown by the existing test asserting the same unredacted field: [8](#0-7)

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

**File:** core/web/resolver/bridge.go (L52-55)
```go
// OutgoingToken resolves the bridge's outgoing token.
func (r *BridgeResolver) OutgoingToken() string {
	return r.bridge.OutgoingToken
}
```

**File:** core/web/resolver/testdata/config-full.toml (L85-98)
```text
[WebServer.LDAP]
ServerTLS = true
SessionTimeout = '15m0s'
QueryTimeout = '2m0s'
BaseUserAttr = 'uid'
BaseDN = ''
UsersDN = 'ou=users'
GroupsDN = 'ou=groups'
ActiveAttribute = ''
ActiveAttributeAllowedValue = ''
AdminUserGroupCN = 'NodeAdmins'
EditUserGroupCN = 'NodeEditors'
RunUserGroupCN = 'NodeRunners'
ReadUserGroupCN = 'NodeReadOnly'
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
