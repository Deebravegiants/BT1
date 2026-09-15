Based on my investigation, I found a valid analog: the chainlink Bridge API exposes a secret authentication token in plaintext on every read of a bridge resource, not just on creation.

### Title
Bridge outgoing token exposed in plaintext on every Index/Show API response - (File: core/web/presenters/bridges.go)

### Summary
The Jenkins advisory describes a stored secret (SMTP password) being echoed back in plaintext into a UI/response that any user with access to the configuration screen could read, beyond the intended one-time reveal at creation. The Chainlink node has a structurally identical pattern for Bridge outgoing tokens: the token is meant to be a secret credential, but the presenter that serializes bridge resources always includes it in plaintext, on every subsequent read, not only at creation.

### Finding Description
`BridgeType.OutgoingToken` is a per-bridge secret token generated at creation time and stored in the DB in plaintext [1](#0-0) , generated via `utils.NewSecret(24)` in `NewBridgeType` [2](#0-1) . Unlike `IncomingToken`, which is hashed for storage and explicitly commented as "only provided when creating a Bridge" with a `json:"incomingToken,omitempty"` tag, `OutgoingToken` is serialized unconditionally (no `omitempty`) in `BridgeResource`: [3](#0-2) 

This presenter is used by both the `Index` (list all bridges) and `Show` (get one bridge) controller actions: [4](#0-3) 

So any authenticated API caller who can hit `GET /v2/bridge_types` or `GET /v2/bridge_types/{name}` receives the plaintext outgoing secret token for every bridge in the system, indefinitely — the same class of bug as the Jenkins issue: a secret value that should only be revealed once (at creation) is instead persistently exposed through a normal read/"configuration form" path.

### Impact Explanation
The `OutgoingToken` is the credential the Chainlink node uses to authenticate itself to the external adapter (bridge) when calling out. Any client with read access to the bridge configuration API can harvest it and impersonate the node to the external adapter, or use it to correlate/attack the bridge integration. This is a direct secret-disclosure issue (CWE-200 analog), matching the "High confidentiality impact, no privilege beyond basic access" profile of the CVSS vector in the report (`C:H/I:N/A:N`).

### Likelihood Explanation
Any user/API key with permission to call the standard bridge listing/show endpoints (which are core, frequently-used node-management endpoints) is exposed to this, no special privilege escalation or admin-only action required. I was unable to fully verify from the router configuration whether these routes require an elevated role versus a lower "view" role before this session ended — this distinction is relevant to precise severity but does not change the core finding that the token is unnecessarily and persistently exposed in the response payload.

### Recommendation
Do not include `OutgoingToken` in the `BridgeResource` used for `Index`/`Show`. Redact it (e.g., mask as `"xxxxx"` similar to `config.SecretString`/`SecretURL` patterns already used elsewhere in the codebase for redaction, see `core/store/models/secrets.go`) except at creation time, mirroring the existing `omitempty`/one-time-reveal treatment already applied to `IncomingToken`.

### Proof of Concept
1. Create a bridge via `POST /v2/bridge_types` with any authenticated session — note the response includes the generated `outgoingToken`.
2. Later, as any client authorized to call `GET /v2/bridge_types` or `GET /v2/bridge_types/{name}`, observe that the same plaintext `outgoingToken` value is returned again in the JSON:API response body, confirming persistent plaintext disclosure via `presenters.NewBridgeResource` [5](#0-4) .

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

**File:** core/web/presenters/bridges.go (L30-41)
```go
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
