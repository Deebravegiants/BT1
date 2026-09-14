### Title
Bridge outgoing webhook token disclosed to any authenticated viewer on every read (Index/Show/GraphQL) instead of only at creation - ([File: core/web/presenters/bridges.go])

### Summary
This is a plausible analog of BIT-gitlab-2022-1413 (missing input masking causing sensitive integration properties to be disclosed in the web interface). In Chainlink, the `BridgeType.OutgoingToken` — a credential the node presents to authenticate itself when the node calls out to an external adapter/bridge — is returned unmasked in every subsequent read of a bridge resource (list, show, GraphQL query), not just at creation time, unlike the `IncomingToken`, which is correctly scoped to `omitempty` and only populated at creation.

### Finding Description
`BridgeType` persists `OutgoingToken` in plaintext in the DB [1](#0-0) . When a bridge is created, `NewBridgeType` generates both an `IncomingToken` (returned only in the one-time creation response, `BridgeTypeAuthentication`) and an `OutgoingToken`, which is stored on `BridgeType` itself [2](#0-1) .

The REST presenter `BridgeResource` marks `IncomingToken` with `json:"incomingToken,omitempty"` and explicitly documents "only provided when creating a Bridge," but `OutgoingToken` has no such restriction — it is a plain `json:"outgoingToken"` field that is always populated from the DB record by `NewBridgeResource` [3](#0-2) .

This resource is used identically for:
- `Create` (expected, one-time reveal) [4](#0-3) 
- `Show` for any bridge by name on every subsequent GET, verified by `TestBridgeController_Show` which fetches an existing bridge from the DB and asserts the resource is returned [5](#0-4) 
- Index/list endpoint (same presenter/DB read pattern) [6](#0-5) 
- The GraphQL `Bridge` type/resolver, which likewise exposes `outgoingToken` unconditionally on every `bridge`/`bridges` query [7](#0-6) [8](#0-7) 

The test suite explicitly documents and asserts this behavior (the token is returned in the plain "read" response, not just the create response) [9](#0-8) .

### Impact Explanation
`OutgoingToken` is a Chainlink-node-held credential used to authenticate itself when calling external adapters/bridges (analogous to GitLab's disclosed "sensitive integration properties"). Persistently exposing this secret on every list/show/GraphQL request — rather than one-time at creation, as is done correctly for `IncomingToken` — expands the exposure window: any caller with read access to bridge resources (e.g., any authenticated UI/API session, or any GraphQL client with query access) can repeatedly retrieve this token, including via logs, browser history/caching of API responses, or any other authenticated party who should not need standing access to the credential. If bridge visibility is not tightly restricted to admins, this constitutes unnecessary and repeated disclosure of a secret used to control interaction with external systems.

### Likelihood Explanation
I was unable to confirm within the available context whether Index/Show routes for `bridge_types` and the GraphQL `bridge`/`bridges` queries require an elevated role (e.g., admin-only) versus being accessible to any authenticated session/API-token holder. My search for role/permission gating on these specific routes in `core/web/router.go` did not resolve conclusively before the tool budget was exhausted; the relevant role-checking calls in `router.go` and `bridge_types_controller.go` matched generic patterns but I couldn't confirm the exact role tier bound to these specific routes. This uncertainty directly affects severity: if only Admin-role users can reach these endpoints, impact is limited to a smaller trust boundary; if any authenticated (including read-only) role can reach them, the disclosure is broader.

### Recommendation
- Do not return `OutgoingToken` in `BridgeResource` for `Show`/`Index` responses; return it only in the one-time `Create` response, mirroring the `IncomingToken` (`omitempty` + creation-only population) pattern.
- Apply the same restriction to the GraphQL `Bridge` type/resolver so `outgoingToken` is only surfaced in `CreateBridgeSuccess`, not in generic `bridge`/`bridges` queries.
- Verify and, if necessary, tighten role requirements on bridge read routes so that only privileged roles can view bridge metadata at all.

### Proof of Concept
1. As any authenticated user with read access to `/v2/bridge_types`, create a bridge (`POST /v2/bridge_types`) and note its name.
2. As the same or another authenticated user with read access, call `GET /v2/bridge_types/{name}` at any later time.
3. Observe the response includes `outgoingToken` with the live plaintext secret [10](#0-9) , exactly as returned at creation — demonstrating the secret is disclosed on every subsequent read, not masked/omitted as `incomingToken` is.
4. Repeat via GraphQL: `query { bridge(id: "name") { outgoingToken } }` returns the same secret on demand [11](#0-10) .

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

**File:** core/web/bridge_types_controller.go (L98-99)
```go
	resource := presenters.NewBridgeResource(*bt)
	resource.IncomingToken = bta.IncomingToken
```

**File:** core/web/bridge_types_controller_test.go (L271-296)
```go
func TestBridgeController_Show(t *testing.T) {
	t.Parallel()

	app := cltest.NewApplication(t)
	require.NoError(t, app.Start(t.Context()))

	client := app.NewHTTPClient(nil)

	bt := &bridges.BridgeType{
		Name:          bridges.MustParseBridgeName(testutils.RandomizeName("showbridge")),
		URL:           cltest.WebURL(t, "https://testing.com/bridges"),
		Confirmations: 0,
	}
	ctx := t.Context()
	require.NoError(t, app.BridgeORM().CreateBridgeType(ctx, bt))

	resp, cleanup := client.Get("/v2/bridge_types/" + bt.Name.String())
	t.Cleanup(cleanup)
	assert.Equal(t, http.StatusOK, resp.StatusCode, "Response should be successful")

	var resource presenters.BridgeResource
	cltest.ParseJSONAPIResponse(t, resp, &resource)
	assert.Equal(t, bt.Name.String(), resource.Name, "should have the same name")
	assert.Equal(t, bt.URL.String(), resource.URL, "should have the same URL")
	assert.Equal(t, bt.Confirmations, resource.Confirmations, "should have the same Confirmations")

```

**File:** core/bridges/orm.go (L108-123)
```go
// BridgeTypes returns bridge types ordered by name filtered limited by the
// passed params.
func (o *orm) BridgeTypes(ctx context.Context, offset int, limit int) (bridges []BridgeType, count int, err error) {
	err = o.transact(ctx, true, func(tx *orm) error {
		if err = tx.ds.GetContext(ctx, &count, "SELECT COUNT(*) FROM bridge_types"); err != nil {
			return pkgerrors.Wrap(err, "BridgeTypes failed to get count")
		}
		sql := `SELECT * FROM bridge_types ORDER BY name asc LIMIT $1 OFFSET $2;`
		if err = tx.ds.SelectContext(ctx, &bridges, sql, limit, offset); err != nil {
			return pkgerrors.Wrap(err, "BridgeTypes failed to load bridge_types")
		}
		return nil
	})

	return
}
```

**File:** core/web/resolver/bridge.go (L52-55)
```go
// OutgoingToken resolves the bridge's outgoing token.
func (r *BridgeResolver) OutgoingToken() string {
	return r.bridge.OutgoingToken
}
```

**File:** core/web/schema/type/bridge.graphql (L1-10)
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
```

**File:** core/web/presenters/bridges_test.go (L24-57)
```go
	bridge := bridges.BridgeType{
		Name:                   "test",
		URL:                    models.WebURL(*url),
		Confirmations:          1,
		OutgoingToken:          "vjNL7X8Ea6GFJoa6PBsvK2ECzNK3b8IZ",
		MinimumContractPayment: assets.NewLinkFromJuels(1),
		UseConnectionManager:   true,
		CreatedAt:              timestamp,
	}

	r := NewBridgeResource(bridge)

	b, err := jsonapi.Marshal(r)
	require.NoError(t, err)

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

**File:** core/web/resolver/bridge_test.go (L86-141)
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
			query: query,
			result: `{
				"bridge": {
					"id": "bridge1",
					"name": "bridge1",
					"url": "https://external.adapter",
					"confirmations": 1,
					"outgoingToken": "outgoingToken",
					"minimumContractPayment": "1",
					"createdAt": "2021-01-01T00:00:00Z"
				}
			}`,
```
