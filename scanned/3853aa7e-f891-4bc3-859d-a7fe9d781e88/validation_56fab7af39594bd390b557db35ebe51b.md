## Analysis

The CVE describes unprivileged users (`Overall/Read`) enumerating credential IDs via HTTP endpoints lacking proper permission checks. The closest analog in this codebase is in the REST and GraphQL bridge APIs, where a low-privileged (`View`-role) authenticated user can read a live bridge secret (`OutgoingToken`) via `GET` endpoints that are explicitly allowed for the lowest-privilege role.

### Title
Bridge `OutgoingToken` secret disclosed to View-role users via `GET /v2/bridge_types` and GraphQL `bridges`/`bridge` queries - (File: core/web/presenters/bridges.go)

### Summary
The `BridgeResource` presenter used by `BridgeTypesController.Index`/`Show` (REST) and the GraphQL `Bridge` type always serialize the `OutgoingToken` field without any role-based restriction, and these read routes are explicitly permitted for the `View` role (the lowest privilege tier), analogous to the Jenkins Kubernetes CLI plugin CVE where `Overall/Read`-level actors could read credential identifiers meant to be restricted to higher-privilege operations.

### Finding Description
`BridgeResource` unconditionally includes `OutgoingToken` (unlike `IncomingToken`, which is `omitempty` and only populated on creation): [1](#0-0) 

`NewBridgeResource` always copies `b.OutgoingToken` into the response for both `Index` (list) and `Show` (single bridge): [2](#0-1) 

The `BridgeTypesController.Index` and `Show` handlers serialize this resource for any authenticated caller, with no additional role check (`auth.RequiresEditRole`/`RequiresAdminRole` wrappers are applied only to `Create`/`Update`/`Destroy`, not `Index`/`Show`): [3](#0-2) 

The project's own RBAC route map explicitly documents that `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` are allowed for `viewOnlyAllowed` (the `View` role — the lowest privilege level, analogous to `Overall/Read`): [4](#0-3) 

The same secret is exposed unconditionally through the GraphQL schema as a non-nullable field on every bridge query (`bridges`, `bridge`), reachable by any session-authenticated GraphQL user regardless of role since `authenticateUser` (used for read queries) only checks session presence, not role: [5](#0-4) [6](#0-5) 

The token itself is a generated secret, stored in plaintext in the DB and used by the node to authenticate itself when responding to bridge/external-adapter callbacks: [7](#0-6) 

### Impact Explanation
Any authenticated user with only `View` role (or any authenticated GraphQL session) can retrieve every configured bridge's `OutgoingToken` by simply calling `GET /v2/bridge_types` or the GraphQL `bridges` query — actions they are explicitly permitted to perform under the RBAC model. This grants a low-privilege actor access to a secret intended to be scoped to bridge management, enabling impersonation of the node in outgoing-token-authenticated callback flows and undermining the RBAC boundary between `View` and `Edit`/`Admin` roles.

### Likelihood Explanation
High likelihood of reachability: the endpoints are part of the standard authenticated REST/GraphQL surface, require no special exploitation, and are explicitly validated in tests to be accessible by `View`-role users. Any node operator granting a `View`-role account (a common "read-only monitoring" grant) inadvertently discloses all bridge outgoing tokens.

### Recommendation
Omit `OutgoingToken` from `Index`/list responses and/or gate its exposure in `Show`/`bridges`/`bridge` behind `Edit`/`Admin` role checks, mirroring the `omitempty`/creation-only treatment already given to `IncomingToken`. If GraphQL parity is required, restrict `outgoingToken` resolution to authorized roles using the existing `authenticateUserCanEdit`/`authenticateUserIsAdmin` helpers rather than the plain `authenticateUser` check.

### Proof of Concept
1. Create a `View`-role API token/session (`sessions.UserRoleView`).
2. `GET /v2/bridge_types` with that session — per `TestRBAC_Routemap_ViewOnly`, this call is expected to succeed (not `401`/`403`).
3. Inspect the JSON response `data[].attributes.outgoingToken` — it contains the live secret token for each configured bridge, as shown being marshaled unconditionally in `presenters/bridges_test.go`: [8](#0-7)

### Citations

**File:** core/web/presenters/bridges.go (L10-21)
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
```

**File:** core/web/presenters/bridges.go (L29-41)
```go
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

**File:** core/web/router.go (L268-273)
```go
		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
```

**File:** core/web/auth/auth_test.go (L227-231)
```go
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
	{"DELETE", "/v2/bridge_types/MOCK", false, false, true},
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

**File:** core/web/resolver/auth.go (L11-17)
```go
// Authenticates the user from the session cookie, presence of user inherently provides 'view' access.
func authenticateUser(ctx context.Context) error {
	if _, ok := auth.GetGQLAuthenticatedSession(ctx); !ok {
		return unauthorizedError{}
	}
	return nil
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

**File:** core/web/presenters/bridges_test.go (L39-55)
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
```
