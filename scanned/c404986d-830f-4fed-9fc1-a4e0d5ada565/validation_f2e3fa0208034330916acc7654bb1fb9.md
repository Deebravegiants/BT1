### Title
Bridge `outgoingToken` credential is stored in plaintext and disclosed to any authenticated viewer-role user - (File: core/web/presenters/bridges.go)

### Summary
Chainlink's bridge subsystem persists the outbound authentication credential (`OutgoingToken`) for external adapters in plaintext in the database, and this credential is served back to any authenticated user holding only the lowest "viewer" role via both the REST API (`GET /v2/bridge_types/:BridgeName`) and the GraphQL `bridge`/`bridges` queries. This mirrors the underlying bug class in GHSA-ph9f-h462-j5jg / CVE-2019-10284 (Jenkins Diawi Upload Plugin): a sensitive credential is stored unencrypted and exposed to users with a lesser read-only permission level rather than being restricted to administrators/editors.

### Finding Description
When a bridge is created, `NewBridgeType` generates two secrets: `IncomingToken` (hashed with a salt before storage, `IncomingTokenHash`) and `OutgoingToken`, which is stored **unhashed** in the `bridge_types.outgoing_token` column: [1](#0-0) [2](#0-1) 

Unlike `IncomingTokenHash`, which is a one-way hash and can never be recovered via the API, `OutgoingToken` is stored and returned as plaintext by the JSONAPI presenter without `omitempty`, on every fetch of a bridge — not just at creation time (`IncomingToken` does have `omitempty` and is only populated on creation): [3](#0-2) 

The REST controller's `Show`/`Index` handlers serialize the full `BridgeType` (including `OutgoingToken`) for any successfully authenticated request: [4](#0-3) 

The router only wraps `GET /v2/bridge_types/:BridgeName` and `GET /v2/bridge_types` behind session/token authentication — no role-elevation check (`auth.RequiresEditRole`/`RequiresAdminRole`) is applied to the read paths, only to `Create`/`Update`/`Destroy`: [5](#0-4) 

The RBAC test table confirms this is by design: the "view" role is explicitly allowed on `GET /v2/bridge_types/MOCK` and `GET /v2/bridge_types`: [6](#0-5) 

The same value is exposed identically through the GraphQL schema/resolver, which returns `outgoingToken: String!` as a non-nullable, always-present field on the `Bridge` type, again reachable by any authenticated GraphQL client regardless of role granularity beyond basic session/token auth: [7](#0-6) [8](#0-7) 

### Impact Explanation
`OutgoingToken` is the shared secret the Chainlink node itself uses when it calls out to an external adapter/bridge (analogous to an outbound API key). Any operator-created "viewer" role account — the lowest privilege authenticated web/API role in Chainlink, intended for read-only monitoring — can retrieve this secret for every configured bridge simply by listing or fetching bridge resources. An attacker who compromises or is issued a low-privilege viewer credential (e.g., a monitoring/dashboard integration, a support account) can exfiltrate every bridge's outgoing credential without needing edit/admin rights, and could use it to impersonate the node when calling the external adapter, or replay/tamper with adapter-facing calls if the adapter trusts that token for authorization. This is a direct secret-disclosure/privilege-boundary issue in the node's own API authorization model, matching the CWE-522 "Insufficiently Protected Credentials" class from the reference advisory.

### Likelihood Explanation
Likelihood is high for any deployment that issues "viewer" role credentials to less-trusted parties (a common practice for dashboards, external monitoring, or read-only operational tooling), since no additional privilege is required beyond a valid, currently-supported session or API token with the `view` role — the exact scenario the RBAC test suite documents as intentionally allowed.

### Recommendation
- Restrict `outgoingToken` exposure in `BridgeResource`/GraphQL `Bridge` type to admin/edit roles only, following the same pattern already used for `IncomingToken` (`omitempty`, creation-only exposure), or omit it from read (`Show`/`Index`/GraphQL `bridge`) responses entirely.
- Consider hashing/encrypting `outgoing_token` at rest (as is already done for the incoming token) and only decrypting/using it internally when the node makes outbound calls, never re-serializing it to API consumers after creation.
- Add explicit RBAC coverage/tests ensuring the outgoing token field is redacted for view-only roles.

### Proof of Concept
1. As an administrator, create a bridge type via `POST /v2/bridge_types`; note the returned `outgoingToken`.
2. Create a user with `viewer` (view-only) role.
3. Authenticate as the viewer user and issue `GET /v2/bridge_types/<bridge_name>` (or the GraphQL `bridge(id: "<bridge_name>")` query).
4. Observe that the response includes the same plaintext `outgoingToken` value returned at creation, despite the requesting user having only read-only privileges — confirmed by the RBAC table marking this route `viewOnlyAllowed: true` [6](#0-5)  and the presenter unconditionally serializing `OutgoingToken` [9](#0-8) .

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

**File:** core/bridges/bridge_type.go (L70-101)
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

**File:** core/web/resolver/bridge.go (L52-55)
```go
// OutgoingToken resolves the bridge's outgoing token.
func (r *BridgeResolver) OutgoingToken() string {
	return r.bridge.OutgoingToken
}
```
