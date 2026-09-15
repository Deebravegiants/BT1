### Title
Bridge OutgoingToken Plaintext Storage and Disclosure to Low-Privilege (View-Role) Users - ([File: core/web/presenters/bridges.go])

### Summary
The Jenkins OpsGenie advisory describes an API key stored unencrypted and disclosed to lower-privileged users than intended. An analogous pattern exists in chainlink's bridge management subsystem: the `OutgoingToken` (a secret credential used to authenticate outgoing requests to external adapters) is stored in plaintext in the database and is unconditionally returned in plaintext on every bridge read (`GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, and the GraphQL `bridge`/`bridges` queries), which are accessible to `view`-role authenticated users.

### Finding Description
`BridgeType.OutgoingToken` is stored as plaintext in the `bridge_types` table (unlike `IncomingTokenHash`, which is hashed with a salt) [1](#0-0) . Every time a bridge is created, the outgoing token is generated in plaintext and persisted directly, with no hashing or encryption applied [2](#0-1) .

The `BridgeResource` presenter — used for both the JSONAPI `GET /v2/bridge_types` (Index) and `GET /v2/bridge_types/:BridgeName` (Show) endpoints — always includes the plaintext `OutgoingToken` field in the response, unconditionally (unlike `IncomingToken`, which is `omitempty` and only populated at creation time): [3](#0-2) 

The same plaintext value is exposed through the GraphQL `BridgeResolver.OutgoingToken()` resolver used by the `bridge`/`bridges` queries [4](#0-3) .

Critically, both the REST `GET /v2/bridge_types` / `GET /v2/bridge_types/:BridgeName` routes and the GraphQL `bridge`/`bridges` queries are reachable by any authenticated user with the lowest privilege level — `view` role — with no elevated role requirement, per the router registration: [5](#0-4) 
and confirmed by the RBAC test matrix, which marks `GET /v2/bridge_types` and `GET /v2/bridge_types/MOCK` as `viewOnlyAllowed: true` [6](#0-5) . GraphQL queries for bridges require only `authenticateUser`, which grants access to any session regardless of role (as opposed to `authenticateUserCanEdit`/`authenticateUserIsAdmin` used for mutations) [7](#0-6) .

This mirrors the OpsGenie bug class: a secret credential (`OutgoingToken`) is (1) stored unencrypted and (2) transmitted in plaintext to a user population (view-role) that is not expected to hold operational secrets — view role is intended for read-only monitoring, not credential management.

### Impact Explanation
Any user granted the minimal `view` role (or a compromised/leaked session with `view` privileges) can read the plaintext `OutgoingToken` for every configured bridge via `GET /v2/bridge_types` or the GraphQL `bridges` query. This token is used by the Chainlink node to authenticate itself to the external adapter when sending outgoing job-run responses/results. Disclosure of this token to an unprivileged viewer allows that actor to impersonate the Chainlink node when communicating with the external adapter (request impersonation), potentially manipulating adapter-side behavior or exfiltrating the secret for further misuse against the connected external adapter infrastructure.

### Likelihood Explanation
High likelihood of reachability: this requires no special privilege beyond having any authenticated session (view role, the lowest tier), and the token is returned by default on the standard list/show endpoints and GraphQL query with no filtering. No additional exploit conditions or timing constraints are needed — this is direct, always-on disclosure by design of the presenter/resolver code.

### Recommendation
- Do not return `OutgoingToken` in plaintext to view-role users; restrict it to `edit`/`admin` roles or omit it from list/show responses entirely (similar to how `IncomingToken` is already `omitempty` and only surfaced at creation).
- Consider storing `OutgoingToken` using the same salted-hash pattern already used for `IncomingTokenHash`, or at minimum encrypt it at rest, and only decrypt/expose to the outbound-request code path.
- Apply the principle already used elsewhere in the codebase (`core/store/models/secrets.go`'s `Secret`/`SecretURL` redaction pattern used for TOML secrets) to bridge/external-initiator credentials returned over the API.

### Proof of Concept
1. Create a session as a user with `UserRoleView`.
2. Issue `GET /v2/bridge_types` (or the GraphQL query `{ bridges { results { outgoingToken } } }`).
3. Observe that the response includes the plaintext `outgoingToken` field for each bridge, per `NewBridgeResource` [8](#0-7)  and the router's unauthenticated-by-role registration of `GET /v2/bridge_types` [9](#0-8) .
4. Use the disclosed `outgoingToken` to impersonate the node when communicating with the configured external adapter.

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

**File:** core/web/resolver/bridge.go (L52-55)
```go
// OutgoingToken resolves the bridge's outgoing token.
func (r *BridgeResolver) OutgoingToken() string {
	return r.bridge.OutgoingToken
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

**File:** core/web/auth/auth_test.go (L227-230)
```go
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
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
