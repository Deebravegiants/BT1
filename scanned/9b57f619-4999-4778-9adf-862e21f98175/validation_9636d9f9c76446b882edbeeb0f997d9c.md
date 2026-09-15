I found a concrete analog: bridge queries in the GraphQL API return the plaintext `OutgoingToken` (the bridge's outbound authentication secret used to call external adapters) to any authenticated user with only the lowest `view` role.

### Title
Bridge Outgoing Token Disclosed in Plaintext to View-Role Users via GraphQL - (File: core/web/resolver/query.go)

### Summary
The `Bridge` and `Bridges` GraphQL queries only require `authenticateUser`, which grants access to any authenticated session regardless of role, including the lowest-privilege `UserRoleView`. These queries return the bridge's `OutgoingToken` in cleartext, which is a credential used by the Chainlink node to authenticate itself to the external adapter (bridge).

### Finding Description
`Resolver.Bridge` and `Resolver.Bridges` in `core/web/resolver/query.go` call only `authenticateUser(ctx)`, the weakest gate that accepts any authenticated session and inherently grants "view" access [1](#0-0) , unlike other resolvers such as `CreateVRFKey`/`DeleteVRFKey` and job proposal mutations, which call `authenticateUserCanEdit` or `authenticateUserIsAdmin` [2](#0-1) . The `BridgeResolver.OutgoingToken()` method exposes the raw token stored on the `bridges.BridgeType` struct without redaction [3](#0-2) , and the underlying `BridgeType.OutgoingToken` field is a plain string column (`outgoing_token`), stored and returned unencrypted, contrasted with `IncomingTokenHash`, which is deliberately hashed [4](#0-3) . The GraphQL schema and generated SDK explicitly expose `outgoingToken` as a queryable field on the `Bridge` type [5](#0-4) , and this is exercised in existing tests confirming any authenticated caller receives the token verbatim [6](#0-5) .

### Impact Explanation
The `OutgoingToken` is the credential the Chainlink node presents to the external adapter (bridge) when making outbound job-pipeline requests. Disclosure of this token to a low-privilege `view`-role user allows that user to impersonate the node when calling the external adapter directly, potentially triggering unauthorized adapter actions, exfiltrating adapter-side data, or abusing rate-limited/paid adapter endpoints attributed to the node's identity — mirroring the CWE-522/CWE-256 class described in the reference advisory (credentials stored/exposed in plaintext, viewable by lower-privileged roles).

### Likelihood Explanation
Any authenticated Chainlink Operator UI/API user, even one provisioned with the lowest `view` role (intended to be read-only and non-sensitive), can call the `bridge`/`bridges` GraphQL queries with no additional privilege check, making exploitation trivial and requiring no special access beyond a valid low-privilege session.

### Recommendation
Redact or omit `OutgoingToken` from the `Bridge`/`Bridges` GraphQL query responses, or restrict retrieval of this field to admin/edit-role sessions via `authenticateUserCanEdit`/`authenticateUserIsAdmin`, consistent with how other sensitive mutations already gate access in `core/web/resolver/auth.go`.

### Proof of Concept
1. Provision a Chainlink node user with `UserRoleView`.
2. Authenticate to the GraphQL API (`/query`) with that view-role session.
3. Execute:
```graphql
query GetBridge {
  bridge(id: "bridge1") {
    ... on Bridge {
      name
      outgoingToken
    }
  }
}
```
4. Observe the plaintext `outgoingToken` returned in the response despite the requester holding only `view` privileges, as demonstrated by the existing test expectations in `core/web/resolver/bridge_test.go` (lines 43-80), which show the token returned verbatim for any `authenticated: true` session without role differentiation.

### Citations

**File:** core/web/resolver/query.go (L27-57)
```go
// Bridge retrieves a bridges by name.
func (r *Resolver) Bridge(ctx context.Context, args struct{ ID graphql.ID }) (*BridgePayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}

	name, err := bridges.ParseBridgeName(string(args.ID))
	if err != nil {
		return nil, err
	}

	bridge, err := r.App.BridgeORM().FindBridge(ctx, name)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return NewBridgePayload(bridge, err), nil
		}

		return nil, err
	}

	return NewBridgePayload(bridge, nil), nil
}

// Bridges retrieves a paginated list of bridges.
func (r *Resolver) Bridges(ctx context.Context, args struct {
	Offset *int32
	Limit  *int32
}) (*BridgesPayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}
```

**File:** core/web/resolver/auth.go (L11-55)
```go
// Authenticates the user from the session cookie, presence of user inherently provides 'view' access.
func authenticateUser(ctx context.Context) error {
	if _, ok := auth.GetGQLAuthenticatedSession(ctx); !ok {
		return unauthorizedError{}
	}
	return nil
}

// Authenticates the user from the session cookie and asserts at least 'run' role.
func authenticateUserCanRun(ctx context.Context) error {
	session, ok := auth.GetGQLAuthenticatedSession(ctx)
	if !ok {
		return unauthorizedError{}
	}
	if session.User.Role == sessions.UserRoleView {
		return RoleNotPermittedError{session.User.Role}
	}
	return nil
}

// Authenticates the user from the session cookie and asserts at least 'edit' role.
func authenticateUserCanEdit(ctx context.Context) error {
	session, ok := auth.GetGQLAuthenticatedSession(ctx)
	if !ok {
		return unauthorizedError{}
	}
	switch session.User.Role {
	case sessions.UserRoleView, sessions.UserRoleRun:
		return RoleNotPermittedError{session.User.Role}
	default:
	}
	return nil
}

// Authenticates the user from the session cookie and asserts has 'admin' role
func authenticateUserIsAdmin(ctx context.Context) error {
	session, ok := auth.GetGQLAuthenticatedSession(ctx)
	if !ok {
		return unauthorizedError{}
	}
	if session.User.Role != sessions.UserRoleAdmin {
		return RoleNotPermittedError{session.User.Role}
	}
	return nil
}
```

**File:** core/web/resolver/bridge.go (L52-55)
```go
// OutgoingToken resolves the bridge's outgoing token.
func (r *BridgeResolver) OutgoingToken() string {
	return r.bridge.OutgoingToken
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

**File:** deployment/environment/web/sdk/internal/genqlient.graphql (L392-400)
```text
fragment BridgeParts on Bridge {
    id
    name
    url
    confirmations
    outgoingToken
    minimumContractPayment
    createdAt
}
```

**File:** core/web/resolver/bridge_test.go (L43-80)
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
