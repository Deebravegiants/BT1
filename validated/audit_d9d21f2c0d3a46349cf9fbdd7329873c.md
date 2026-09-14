## Analog Vulnerability Found

### Title
Bridge `OutgoingToken` secret is returned unmasked in plaintext on every bridge list/view/update/delete API and GraphQL response - ([File: core/web/presenters/bridges.go])

### Summary
The Jenkins Applitools Eyes advisory describes a job configuration form that displays a stored API key/secret in plaintext instead of masking it, letting anyone who can view the job configuration observe the credential. Chainlink has a directly analogous pattern: the bridge's `OutgoingToken` — a secret credential used to authenticate outbound requests to the external adapter — is unconditionally serialized in plaintext in the `BridgeResource` presenter and returned on every bridge read/list/update/delete REST and GraphQL call, not just on creation.

### Finding Description
`BridgeType.OutgoingToken` is a persisted secret (`db:"outgoing_token"`) generated at bridge creation time via `utils.NewSecret(24)`: [1](#0-0) [2](#0-1) 

Unlike `IncomingToken`, which the presenter marks `omitempty` and only populates on the `Create` response, `OutgoingToken` has no such guard and is always included: [3](#0-2) 

Every controller action that returns a `BridgeResource` — `Index` (list all bridges), `Show` (get one bridge), `Update`, and `Destroy` — re-serializes the full `BridgeType` including the plaintext `OutgoingToken`, not just at creation time: [4](#0-3) [5](#0-4) 

The same field is exposed via the GraphQL `Bridge` type as a non-nullable `outgoingToken: String!`, confirming the leak is present across both the REST JSON:API and GraphQL surfaces: [6](#0-5) 

The unit test for the presenter demonstrates this behavior is intentional/expected as currently implemented — `outgoingToken` is asserted present in the normal (non-creation) JSON output: [7](#0-6) 

This mirrors the CWE-522 pattern in the Jenkins advisory: a secret that should only be revealed once (or masked thereafter) is instead persistently displayed unmasked whenever the "configuration" (here, the bridge resource) is viewed.

### Impact Explanation
`OutgoingToken` is sent by the Chainlink node as a bearer credential to the configured external adapter URL on every bridge task execution, so its disclosure lets anyone who can view bridge configuration impersonate the node when calling that external adapter, or replay/observe the credential for further misuse against the adapter endpoint. Any user account or API client with read access to `/v2/bridge_types` (or the equivalent GraphQL `bridges`/`bridge` queries) — not only the bridge creator or an administrative/edit role — obtains the live secret, which is a broader disclosure surface than intended, matching CVSS vector `C:L` in the referenced advisory (confidentiality impact, no privileges beyond authenticated access required to read).

### Likelihood Explanation
Any authenticated node operator (including lower-privileged "view" role users, subject to whatever RBAC gate is applied to the bridge routes) who can call the bridge list/show endpoints will receive the token by default with no special action needed — this is the standard/expected response shape as shown by the existing test fixture, making exploitation trivial and always reachable once basic read access is granted.

### Recommendation
- Only return `OutgoingToken` in the response to bridge creation (as is already done for `IncomingToken`), and mask/omit it (e.g., redact to `xxxxx` or omit the field) on `Index`, `Show`, `Update`, and `Destroy` responses and in the GraphQL `Bridge` type.
- If the token must be surfaced for legitimate rotation/troubleshooting flows, gate it behind an explicit "reveal" action restricted to elevated roles with audit logging, consistent with how `IncomingToken` is handled.

### Proof of Concept
1. As any authenticated user able to call `GET /v2/bridge_types` or `GET /v2/bridge_types/:BridgeName`, issue the request against a node with at least one configured bridge.
2. Observe the JSON:API response body includes `"outgoingToken": "<plaintext-secret>"` for every returned bridge, exactly as encoded by `presenters.NewBridgeResource` and validated by the existing test: [8](#0-7) 
3. Use the captured `outgoingToken` value to authenticate as the node when calling the external adapter endpoint configured for that bridge.

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

**File:** core/web/bridge_types_controller.go (L148-192)
```go
// Update can change the restricted attributes for a bridge
func (btc *BridgeTypesController) Update(c *gin.Context) {
	ctx := c.Request.Context()
	name := c.Param("BridgeName")
	btr := &bridges.BridgeTypeRequest{}

	taskType, err := bridges.ParseBridgeName(name)
	if err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	orm := btc.App.BridgeORM()
	bt, err := orm.FindBridge(ctx, taskType)
	if errors.Is(err, sql.ErrNoRows) {
		jsonAPIError(c, http.StatusNotFound, errors.New("bridge not found"))
		return
	}
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	if err := c.ShouldBindJSON(btr); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}
	if err := ValidateBridgeType(btr); err != nil {
		jsonAPIError(c, http.StatusBadRequest, err)
		return
	}
	if err := orm.UpdateBridgeType(ctx, &bt, btr); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	btc.App.GetAuditLogger().Audit(audit.BridgeUpdated, map[string]any{
		"bridgeName":                   bt.Name,
		"bridgeConfirmations":          bt.Confirmations,
		"bridgeMinimumContractPayment": bt.MinimumContractPayment,
		"bridgeURL":                    bt.URL,
	})

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
