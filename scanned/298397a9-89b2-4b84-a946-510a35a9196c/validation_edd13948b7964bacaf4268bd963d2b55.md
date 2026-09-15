### Title
Bridge `OutgoingToken` Credential Exposed to Any Authenticated User via Bridge Read APIs - ([File: core/web/presenters/bridges.go])

### Summary
Chainlink bridges (external adapters) are configured with an `OutgoingToken`, a credential the node uses to authenticate itself when it calls the external adapter [1](#0-0) . This token is persisted and then returned in full, unredacted, by every bridge read path — the REST `/v2/bridge_types` index/show endpoints and the GraphQL `bridges`/`bridge`/`updateBridge` queries — to any authenticated node API user, not only the operator who created the bridge.

### Finding Description
`BridgeTypeAuthentication`/`BridgeType` store `OutgoingToken` in plaintext in the database [2](#0-1) . Unlike `IncomingTokenHash`, which is hashed and salted for verification of inbound webhook calls, `OutgoingToken` is stored and served back verbatim.

The JSON:API presenter always includes `outgoingToken` in its response payload (confirmed via the presenter marshal test, which shows `outgoingToken` present in the base resource without any special-casing, unlike `incomingToken` which is only attached conditionally on creation) [3](#0-2) .

The GraphQL schema hard-codes `outgoingToken: String!` as a non-nullable field on the `Bridge` type, returned by the `bridges` list query, single `bridge` query, and `updateBridge` mutation [4](#0-3) . The resolver test confirms this credential is returned to any `authenticated: true` session with no additional authorization/role narrowing applied in the test harness [5](#0-4) .

This mirrors the CWE-522 pattern in the reference advisory: a credential needed to authenticate to an external system is stored and exposed to a broader set of principals (any Extended-Read/authenticated user) than the set of principals who legitimately need to know it (the party performing bridge creation/administration).

### Impact Explanation
Any authenticated node-API user who can read bridge configuration (index/show REST endpoints or the `bridges`/`bridge` GraphQL queries) obtains the `OutgoingToken` for every configured bridge. Since this token authenticates the node to the external adapter, its disclosure allows a lower-privileged, unprivileged-relative-to-bridge-management user to impersonate the Chainlink node when calling that external adapter, potentially triggering unauthorized external-adapter actions or corrupting job pipeline behavior depending on how the adapter uses the token.

### Likelihood Explanation
Any authenticated session with read access to bridges (which is a common, low-friction permission on Chainlink node UIs/API) can trivially retrieve this data by issuing a `GET /v2/bridge_types` or a `bridges` GraphQL query — no special exploitation technique is required, only normal API usage.

### Recommendation
Do not return `OutgoingToken` in bridge list/show responses. Only return it once at creation time (as is already done for `IncomingToken`), and require re-authentication/an explicit reveal action gated to an elevated role for subsequent retrieval, mirroring how `IncomingToken` is currently handled [6](#0-5) .

### Proof of Concept
1. Authenticate as any node-API user with bridge read permission.
2. Call `GET /v2/bridge_types/<name>` or run the GraphQL query:
```graphql
query { bridges { results { id name outgoingToken } } }
```
3. Observe the plaintext `outgoingToken` value returned for every bridge, as demonstrated by the resolver test fixture [7](#0-6) .

Note: I was unable to confirm within the available tool calls whether Chainlink's role-based middleware (Admin/Edit/View) restricts the bridge read routes to a subset of authenticated users, since `core/web/router.go`'s exact route-to-role mapping for `bridge_types` was not retrieved before the session ended. If bridge reads are restricted to Admin-only, the practical severity is reduced; if View-role users can read bridges (which is the common configuration for read-only dashboards), the finding stands as described.

### Citations

**File:** core/bridges/bridge_type.go (L44-53)
```go
// BridgeTypeAuthentication is the record returned in response to a request to create a BridgeType
type BridgeTypeAuthentication struct {
	Name                   BridgeName
	URL                    models.WebURL
	Confirmations          uint32
	IncomingToken          string
	OutgoingToken          string
	MinimumContractPayment *assets.Link
	UseConnectionManager   bool `json:"useConnectionManager"`
}
```

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

**File:** core/web/bridge_types_controller.go (L97-99)
```go
	}
	resource := presenters.NewBridgeResource(*bt)
	resource.IncomingToken = bta.IncomingToken
```
