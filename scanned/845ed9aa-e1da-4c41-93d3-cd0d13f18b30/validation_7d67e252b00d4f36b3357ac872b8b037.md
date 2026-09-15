The evidence supports a legitimate analog. In chainlink, bridge credentials are asymmetric: the `IncomingToken` is hashed with a salt before storage, but the `OutgoingToken` is stored and returned as plaintext, and it is exposed via GET endpoints reachable by the lowest-privileged authenticated role (View-only).

### Title
Bridge `OutgoingToken` credential stored and exposed in plaintext to View-only role users - (File: `core/web/bridge_types_controller.go`)

### Summary
The `BridgeType.OutgoingToken` — a secret credential the Chainlink node uses to authenticate itself to external adapters — is persisted unencrypted in the database and returned unmasked by the `GET /v2/bridge_types` (Index) and `GET /v2/bridge_types/:BridgeName` (Show) API endpoints. Unlike `IncomingToken`, which is hashed with a salt (`IncomingTokenHash`/`Salt`), `OutgoingToken` is stored and serialized in plaintext, and these read endpoints are accessible to the lowest-privileged authenticated "View-only" role, not just Admin/Edit roles.

### Finding Description
`bridges.NewBridgeType` generates `OutgoingToken` and stores it verbatim on the `BridgeType` struct (`db:"outgoing_token"`), with no hashing applied, in contrast to `IncomingToken`, which is only ever kept as a salted hash (`IncomingTokenHash`) [1](#0-0) .

The `BridgeResource` presenter marshals `OutgoingToken` unconditionally (no `omitempty`, no redaction), while `IncomingToken` is only populated on creation [2](#0-1) .

The `Index` and `Show` handlers on `BridgeTypesController` fetch the bridge from the ORM and directly wrap it in `presenters.NewBridgeResource`, returning the plaintext `outgoingToken` field in the JSON response for any request to list or view bridges [3](#0-2) .

The RBAC route map explicitly documents that `GET /v2/bridge_types` and `GET /v2/bridge_types/MOCK` are allowed for the `viewOnlyAllowed` role (the least-privileged authenticated role), alongside edit and admin roles [4](#0-3) . This mirrors the Jenkins Deploy-to-container advisory pattern, where the read-only/"Extended Read" role could retrieve credentials that should require higher privilege.

### Impact Explanation
Any operator account provisioned with the low-privilege "View" role (e.g., an auditor or read-only monitoring account) can retrieve the `outgoingToken` for every configured bridge without needing edit/admin rights. This token is used to authenticate outbound requests from the node to the external adapter; disclosure allows a View-role user (or anyone who compromises a View-role session/API key) to impersonate the node when calling the external adapter or to replay/misuse the credential outside the node, exceeding the intended trust boundary of the View role.

### Likelihood Explanation
Any node operator that provisions a read-only/View credential for dashboards, third-party monitoring, or delegated visibility will unintentionally leak all bridge outgoing tokens through a normal, already-permitted GET request — no exploitation of a separate bug is required, only reliance on the documented role model.

### Recommendation
- Do not include `OutgoingToken` in the `BridgeResource` returned from `Index`/`Show` for View-role callers; only return it to Admin/Edit roles, similar to how `IncomingToken` is only returned once, at creation time.
- Alternatively, redact/mask `OutgoingToken` in list/show responses and only expose it via UpdateAllowed endpoints or a dedicated retrieval process. Consider migrating `OutgoingToken` handling to encrypted-at-rest storage, consistent with the intent behind hashing `IncomingToken`.

### Proof of Concept
1. Create a node user session with the "View" role only.
2. Call `GET /v2/bridge_types` (or `GET /v2/bridge_types/<name>`) with that session.
3. Observe the JSON response includes `"outgoingToken": "<plaintext token>"` for each configured bridge, per `NewBridgeResource` [5](#0-4)  and the `Index`/`Show` handlers [6](#0-5) , confirming a View-only account can extract external-adapter credentials it should not be able to see.

### Citations

**File:** core/bridges/bridge_type.go (L55-101)
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

**File:** core/web/auth/auth_test.go (L227-231)
```go
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
	{"DELETE", "/v2/bridge_types/MOCK", false, false, true},
```
