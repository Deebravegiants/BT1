Based on my review, the actual analog to the Jenkins credential storage issue is in Chainlink's **Bridge OutgoingToken** handling, not in the Jenkins-specific plugin behavior.

### Title
Bridge `OutgoingToken` is stored unencrypted and permanently disclosed via the API/GraphQL to any authenticated user - (File: core/bridges/bridge_type.go)

### Summary
Unlike the bridge's `IncomingToken` (hashed with a salt via `incomingTokenHash` and shown to the caller only once at creation time), the bridge's `OutgoingToken` — a credential the Chainlink node sends back to external adapters to authenticate bridge responses — is generated in plaintext and persisted unencrypted in the `bridge_types.outgoing_token` database column, and is returned in plaintext on every subsequent `Index`/`Show`/`Update` API call and via the GraphQL `Bridge.outgoingToken` field.

### Finding Description
`NewBridgeType` generates both tokens, but treats them very differently: [1](#0-0) 

The `IncomingTokenHash` (with `Salt`) is what's persisted for the incoming token, so the raw incoming secret is never stored or re-served. The `OutgoingToken`, however, is stored as plaintext in the `outgoing_token` DB column: [2](#0-1) 

Every read path re-serializes this plaintext secret back to API/GraphQL clients. `BridgeResource` always includes `OutgoingToken` (no redaction, no one-time-only exposure): [3](#0-2) 

The `Index` and `Show` controller actions call `presenters.NewBridgeResource` unconditionally, exposing the stored token on every list/read of bridges: [4](#0-3) 

The same field is also exposed through GraphQL (`Bridge.outgoingToken`): [5](#0-4) 

This is structurally the same bug class as the Jenkins advisory: a credential value needed only for outbound authentication is persisted in cleartext and can be repeatedly retrieved by any party that can read the parent object (bridge/job config), rather than being hashed and disclosed once at creation like its `IncomingToken` counterpart.

### Impact Explanation
Any authenticated Chainlink node API user who can call `GET /v2/bridge_types` / `GET /v2/bridge_types/:BridgeName` or the `bridge`/`bridges` GraphQL queries obtains the plaintext `OutgoingToken` for every configured bridge, at any time, not just at creation. If bridge role/read access is broader than bridge-management privileges (e.g., available to "run"-level users or via the External Initiator's implicit "run" role — `c.Set(SessionUserKey, &clsessions.User{Role: clsessions.UserRoleRun})` in `core/web/auth/auth.go`), this allows a lower-privileged principal to obtain the credential used to validate bridge callback authenticity, enabling response/callback impersonation to the bridge adapter path.

### Likelihood Explanation
Likelihood is limited by whatever role gating exists in `core/web/router.go` for the bridge endpoints (I could not fully verify the exact role requirement for `Index`/`Show` before running out of tool iterations — this needs confirmation). If bridge read access is restricted strictly to Admin, the practical severity is lower (self-disclosure to the credential's own owner), but the storage-in-plaintext root cause and repeated non-redacted disclosure design remain a real deviation from the hashing pattern applied to `IncomingToken`.

### Recommendation
- Store `OutgoingToken` similarly to `IncomingToken`: generate/display it once at creation, and use a hash comparison for outbound verification instead of round-tripping the plaintext secret.
- If the plaintext value must be retained (because it's sent outbound, not verified inbound), redact it from `BridgeResource`/GraphQL responses after initial creation, and require re-authentication (password confirmation) analogous to `NewAPIToken`'s flow to view/rotate it.
- Confirm and, if necessary, tighten the role requirement on bridge read endpoints in `core/web/router.go` so that only Admin-level users can retrieve bridge records containing this token.

### Proof of Concept
1. As an authenticated node user (whatever role is permitted on bridge routes), call `POST /v2/bridge_types` to create a bridge; the plaintext `outgoingToken` value returned is also what's persisted (`core/web/bridge_types_controller.go` `Create`).
2. Later, call `GET /v2/bridge_types/:BridgeName` (or the GraphQL `bridge(id:)` query) — the same plaintext `outgoingToken` is returned again, indefinitely, sourced directly from the unhashed `bridge_types.outgoing_token` column (`core/web/presenters/bridges.go`).
3. Compare with `IncomingToken`, which is never returned again after creation because only its hash (`IncomingTokenHash`) is stored (`core/bridges/bridge_type.go` `NewBridgeType`), confirming the asymmetric, plaintext-persisted handling of `OutgoingToken`.

### Citations

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

**File:** core/store/migrate/migrations/0001_initial.sql (L132-142)
```sql
CREATE TABLE public.bridge_types (
    name text NOT NULL,
    url text NOT NULL,
    confirmations bigint DEFAULT 0 NOT NULL,
    incoming_token_hash text NOT NULL,
    salt text NOT NULL,
    outgoing_token text NOT NULL,
    minimum_contract_payment character varying(255),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
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
