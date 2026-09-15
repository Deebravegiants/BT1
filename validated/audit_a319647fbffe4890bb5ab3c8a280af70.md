Audit Report

## Title
Bridge `OutgoingToken` Credential Exposed to Any Authenticated User via Bridge Read APIs - ([File: core/web/presenters/bridges.go])

## Summary
Bridge `OutgoingToken` values (credentials used by the node to authenticate to external adapters) are persisted in plaintext and returned unredacted by the REST `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` endpoints and the GraphQL `bridges`/`bridge`/`updateBridge`/`createBridge` operations. Confirmed against `core/web/router.go`, these two GET routes carry no role restriction beyond session/token authentication, unlike nearly every other route in the file which is wrapped in `auth.RequiresEditRole`/`auth.RequiresAdminRole`.

## Finding Description
`BridgeType.OutgoingToken` is stored in plaintext [1](#0-0) , and `NewBridgeResource` always copies it into the JSON:API response with no redaction, contrasted with `IncomingToken`, which is `omitempty` and only populated at creation time [2](#0-1) . The presenter marshal test confirms `outgoingToken` appears in every serialized bridge resource [3](#0-2) .

Critically, I verified the route wiring in `core/web/router.go`: `authv2.GET("/bridge_types", paginatedRequest(bt.Index))` and `authv2.GET("/bridge_types/:BridgeName", bt.Show)` have **no** `auth.RequiresEditRole`/`auth.RequiresAdminRole` wrapper, while the sibling mutating routes (`POST`, `PATCH`, `DELETE` on the same resource) are all wrapped in `auth.RequiresEditRole` [4](#0-3) . This means any session that merely passes `auth.Authenticate` (i.e., any role including a low-privilege View-only account) can read bridge configuration and obtain the plaintext `OutgoingToken`. This closes the previously-noted gap in the original report — the role-mapping was ambiguous there, but it is now confirmed: there is no role gate on bridge reads at all.

The GraphQL schema mirrors this: `outgoingToken: String!` is non-nullable on `Bridge` and returned by `bridges`, `bridge`, `createBridge`, and `updateBridge` [5](#0-4) , resolved directly from the stored field with no redaction [6](#0-5) , and the resolver test harness only requires `authenticated: true`, with no additional role check exercised [7](#0-6) . GraphQL access in `router.go` is likewise gated only by `auth.AuthenticateGQL`, not role-specific middleware [8](#0-7) .

Existing mitigations for the analogous `IncomingToken`/`IncomingTokenHash` (hash-and-salt storage, one-time disclosure at creation only) do not apply to `OutgoingToken`, which is stored in reversible plaintext and always echoed back [9](#0-8) .

## Impact Explanation
This is a credential-exfiltration issue in scope under key/secret exfiltration: any authenticated node-API principal — including a View-only user with no bridge-management authorization — can retrieve the plaintext `OutgoingToken` for every configured bridge via a normal read request. This token authenticates the node to the external adapter, so disclosure permits an unprivileged-relative-to-bridge-administration user to impersonate the node's outbound authentication to that adapter.

## Likelihood Explanation
High feasibility: no special technique is needed. A single authenticated session (any role, since the GET routes have no `RequiresEditRole`/`RequiresAdminRole` wrapper) can issue `GET /v2/bridge_types` or the GraphQL `bridges` query and receive the full plaintext credential for every bridge, confirmed by the router configuration [4](#0-3)  and by the resolver/presenter tests showing the token in the returned payload without any special-casing [10](#0-9) .

## Recommendation
- Do not return `OutgoingToken` on `GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, or the `bridges`/`bridge`/`updateBridge` GraphQL fields.
- Only surface it once, at creation (mirroring `IncomingToken`'s `omitempty`/create-only pattern) [11](#0-10) .
- If continued read access is required, gate it behind `auth.RequiresAdminRole` (as is done for key export/import routes) rather than leaving it open to any authenticated session [12](#0-11) .
- Consider making the GraphQL `outgoingToken` field nullable/omitted outside of creation flows, matching `incomingToken` handling in the schema.

## Proof of Concept
1. Create any authenticated session (any role — no `RequiresEditRole`/`RequiresAdminRole` is enforced on these GET routes per `core/web/router.go` lines 269–271).
2. `GET /v2/bridge_types/<name>` — response includes `attributes.outgoingToken` in plaintext, per `core/web/presenters/bridges_test.go` lines 39–57.
3. Or run the GraphQL query:
```graphql
query { bridges { results { id name outgoingToken } } }
```
matching the fixture in `core/web/resolver/bridge_test.go` lines 18–84, which returns the raw `outgoingToken` value to any `authenticated: true` session.
4. A Go integration test extending `TestBridgeTypesController_Index` (`core/web/bridge_types_controller_test.go`) with a low-privilege/View-role session and an assertion that `outgoingToken` is present in the response would concretely demonstrate the cross-role disclosure.

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

**File:** core/web/router.go (L95-99)
```go
	api.POST("/query",
		auth.AuthenticateGQL(app.AuthenticationProvider(), app.GetLogger().Named("GQLHandler")),
		loader.Middleware(app),
		graphqlHandler(app),
	)
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

**File:** deployment/environment/web/sdk/internal/schema.graphql (L118-126)
```text
type Bridge {
    id: ID!
    name: String!
    url: String!
    confirmations: Int!
    outgoingToken: String!
    minimumContractPayment: String!
    createdAt: Time!
}
```

**File:** core/web/resolver/bridge.go (L52-55)
```go
// OutgoingToken resolves the bridge's outgoing token.
func (r *BridgeResolver) OutgoingToken() string {
	return r.bridge.OutgoingToken
}
```

**File:** core/web/resolver/bridge_test.go (L44-80)
```go
	testCases := []GQLTestCase{
		unauthorizedTestCase(GQLTestCase{query: query}, "bridges"),
		{
			name:          "success",
			authenticated: true,
			before: func(ctx context.Context, f *gqlTestFramework) {
				f.App.On("BridgeORM").Return(f.Mocks.bridgeORM)
				f.Mocks.bridgeORM.On("BridgeTypes", mock.Anything, PageDefaultOffset, PageDefaultLimit).Return([]bridges.BridgeType{
					{
						Name:                   "bridge1",
						URL:                    models.WebURL(*bridgeURL),
						Confirmations:          uint32(1),
						OutgoingToken:          "outgoingToken",
						MinimumContractPayment: assets.NewLinkFromJuels(1),
						CreatedAt:              f.Timestamp(),
					},
				}, 1, nil)
			},
			query: query,
			result: `
			{
				"bridges": {
					"results": [{
						"id": "bridge1",
						"name": "bridge1",
						"url": "https://external.adapter",
						"confirmations": 1,
						"outgoingToken": "outgoingToken",
						"minimumContractPayment": "1",
						"createdAt": "2021-01-01T00:00:00Z"
					}],
					"metadata": {
						"total": 1
					}
				}
			}`,
		},
```
