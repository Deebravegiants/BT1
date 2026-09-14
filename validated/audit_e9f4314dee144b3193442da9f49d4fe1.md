## Title
Bridge `OutgoingToken` credential exposed in plaintext to unprivileged "view"-role users via unrestricted `GET /v2/bridge_types` endpoints - (File: core/web/router.go, core/web/bridge_types_controller.go, core/web/presenters/bridges.go)

### Summary
The Chainlink node's bridge management REST/GraphQL API returns the `OutgoingToken` — the credential the node uses to authenticate itself to the external adapter — in cleartext on every `Index`/`Show` response, and these read endpoints are gated only by `auth.Authenticate` (any logged-in session/API-token), not by `auth.RequiresEditRole`/`RequiresAdminRole`. Any authenticated node user with the lowest ("view") role can therefore retrieve any other bridge's outgoing authentication secret.

### Finding Description
`BridgeTypesController.Index` and `.Show` are registered without a role-restricting middleware, unlike `Create`, `Update`, and `Destroy`: [1](#0-0) 

The presenter used by both of these endpoints unconditionally serializes `OutgoingToken` (`json:"outgoingToken"`, no `omitempty`) into the JSON response body: [2](#0-1) 

`OutgoingToken` is the real secret the node presents to the external adapter to authenticate outbound webhook calls (it is stored server-side and reused, unlike `IncomingToken`, which is only a hash on record and thus intentionally shown once at creation): [3](#0-2) 

The equivalent GraphQL schema/resolver path exposes the same field with no access-control distinction from public bridge metadata: [4](#0-3) [5](#0-4) 

This mirrors the CVE-2020-2153 bug class: a configuration/job-related credential (there, Jenkins Backlog plugin credentials in job config forms; here, the bridge's `OutgoingToken`) is transmitted in plain text as part of a configuration-retrieval response, reachable by an actor who should not have access to that secret. The generic request/response redaction filter (`isBlacklisted`) that the router applies to logged bodies only recognizes password-like keys and does not cover `outgoingToken`/`incomingToken`, reinforcing that this credential class was never treated as sensitive in this code path: [6](#0-5) 

### Impact Explanation
A node operator who grants a colleague or automation a low-privilege "view" role (intended for read-only monitoring, no config-editing rights) inadvertently grants that principal the ability to read every bridge's `OutgoingToken`. That token can then be used to impersonate the Chainlink node when calling out to the external adapter (or replay/misuse whatever bearer-style auth the adapter enforces on outgoing calls), which is a credential-disclosure / privilege-escalation-adjacent issue even though it does not by itself let the attacker call back into the node.

### Likelihood Explanation
Exploitation only requires a valid, low-privilege authenticated session or API key — no special role, and no interaction with the bridge owner. Any environment that provisions "view" role accounts (a supported, documented role) for dashboards/monitoring is exposed by design, making this trivially reachable in normal multi-user deployments.

### Recommendation
Gate `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` (and the equivalent GraphQL bridge queries) behind `auth.RequiresEditRole` (or `RequiresAdminRole`), matching the mutation endpoints, or strip `OutgoingToken` from the presenter for read/list responses and only return it at creation/rotation time, consistent with how `IncomingToken` is already treated (`omitempty`, populated only on create).

### Proof of Concept
1. Create a Chainlink node user with role `view` only.
2. As an admin, create a bridge (`POST /v2/bridge_types`), noting it stores a real `OutgoingToken`.
3. Log in as the `view`-role user and call `GET /v2/bridge_types/<name>` (or `GET /v2/bridge_types`).
4. Observe the response includes `"outgoingToken": "<secret>"` even though this role has no edit/admin rights, per the route wiring: [1](#0-0)

### Citations

**File:** core/web/router.go (L268-273)
```go
		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
```

**File:** core/web/router.go (L643-658)
```go
// NOTE: keys must be in lowercase for case insensitive match
var blacklist = map[string]struct{}{
	"password":             {},
	"newpassword":          {},
	"oldpassword":          {},
	"current_password":     {},
	"new_account_password": {},
}

func isBlacklisted(k string) bool {
	lk := strings.ToLower(k)
	if _, ok := blacklist[lk]; ok || strings.Contains(lk, "password") {
		return true
	}
	return false
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

**File:** core/bridges/bridge_type.go (L44-101)
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
