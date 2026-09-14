### Title
Bridge `outgoingToken` is returned unmasked in read-only API/GraphQL responses, exposing a live authentication secret to any user with view access - (File: core/web/presenters/bridges.go, core/web/resolver/bridge.go)

### Summary
Chainlink's Bridge feature is functionally analogous to the Jenkins Report Portal plugin: it stores a secret token used to authenticate calls to an external system (the External Adapter), and that secret is displayed in plaintext in the node's management UI/API responses. Just like the Jenkins advisory (CVE-2023-30524), where the plugin failed to mask the access token in the configuration form, chainlink's bridge presenter and GraphQL resolver return the `OutgoingToken` field unmasked on every read (`Show`/`Index`/`bridge`/`bridges` queries), not only at creation time.

### Finding Description
`BridgeType.OutgoingToken` is the token chainlink itself sends to the External Adapter (used for adapter-side authentication) [1](#0-0) . Unlike `IncomingToken`, which is properly hashed at rest and only exposed once at creation (via `BridgeTypeAuthentication`) [2](#0-1) , `OutgoingToken` is stored and returned in plaintext.

The REST presenter always includes it, without `omitempty` or redaction, unlike `IncomingToken` which is explicitly commented as "only provided when creating a Bridge": [3](#0-2) 

This presenter is used for both `Show` (single bridge by name) and `Index` (paginated listing of all bridges) controller actions, meaning any authenticated caller who can hit `GET /v2/bridge_types` or `GET /v2/bridge_types/:name` receives the live outgoing token in the JSON response: [4](#0-3) 

The GraphQL resolver mirrors this behavior — `OutgoingToken()` returns the raw token for both the `bridge` and `bridges` queries, with no masking logic: [5](#0-4) 

Tests explicitly confirm the token is returned in full on every read path (`Test_Bridges`, `Test_Bridge`, `Test_UpdateBridge`, `Test_DeleteBridgeMutation`) and in the REST JSON API test (`TestBridgeResource`): [6](#0-5) [7](#0-6) 

The CLI's own table renderer even acknowledges the sensitivity of this data — the multi-row `RenderTable` implementation for `BridgePresenters` intentionally omits `OutgoingToken` from the summary listing to avoid over-exposure, while the single-resource `RenderTable` still prints it in full: [8](#0-7) 

This is the same root-cause bug class as the Jenkins advisory: a secret credential used to authenticate to an external system is not masked when the configuration is displayed to a user via the management interface, and is retrievable on every subsequent read, not just once at creation.

### Impact Explanation
The `outgoingToken` is what chainlink attaches to requests sent to the configured External Adapter URL; anyone who obtains it can potentially replay or forge requests that the adapter will treat as originating from the legitimate chainlink node, or otherwise abuse the adapter's trust relationship with the node. Any authenticated node user (whose access level would ordinarily be scoped to lower-privilege "view" operations, analogous to Jenkins' "Item/Extended Read") who can list or view bridges gains access to this live secret indefinitely, not just at bridge-creation time.

### Likelihood Explanation
I was unable to fully confirm within available context what role/permission level is required to call the `GET /v2/bridge_types*` REST endpoints or the `bridge`/`bridges` GraphQL queries — the router role-gating logic (`core/web/router.go`, `core/web/auth/auth.go`) was only partially inspected before running out of investigation budget. If, as is typical for this kind of resource-listing endpoint, a "view"/read-only role can hit these routes, then likelihood is high, since no special privilege beyond basic node access is needed and the exposure happens on every normal read, not requiring any special exploit conditions.

### Recommendation
- Do not return `OutgoingToken` in full on `Show`/`Index` REST responses or `bridge`/`bridges` GraphQL queries; mask/redact it (e.g., show only a prefix/suffix or a boolean "configured" flag) except at creation/rotation time, mirroring how `IncomingToken` is already handled with `omitempty` and one-time exposure.
- If some privileged workflows still need to view or rotate the outgoing token, gate that behind a distinct, higher-privilege action (e.g., a dedicated "reveal token" endpoint) rather than embedding it in general list/show responses.
- Audit the CLI `BridgePresenter.RenderTable` and GraphQL `BridgeParts` fragment usage across `deployment/environment/web/sdk` for the same unmasked propagation.

### Proof of Concept
1. Authenticate as any node user with permission to call bridge read endpoints.
2. `GET /v2/bridge_types/<bridge-name>` (or run the equivalent `bridges`/`bridge` GraphQL query).
3. Observe the JSON response includes `"outgoingToken": "<plaintext-secret>"` as shown by the presenter and resolver tests: [7](#0-6) [9](#0-8) 
4. The secret can be captured for reuse against the configured external adapter without needing to trigger bridge creation.

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

**File:** core/web/presenters/bridges.go (L16-21)
```go
	// The IncomingToken is only provided when creating a Bridge
	IncomingToken          string       `json:"incomingToken,omitempty"`
	OutgoingToken          string       `json:"outgoingToken"`
	MinimumContractPayment *assets.Link `json:"minimumContractPayment"`
	UseConnectionManager   bool         `json:"useConnectionManager"`
	CreatedAt              time.Time    `json:"createdAt"`
```

**File:** core/web/bridge_types_controller.go (L112-146)
```go
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

**File:** core/web/resolver/bridge.go (L52-55)
```go
// OutgoingToken resolves the bridge's outgoing token.
func (r *BridgeResolver) OutgoingToken() string {
	return r.bridge.OutgoingToken
}
```

**File:** core/web/resolver/bridge_test.go (L121-141)
```go
				f.Mocks.bridgeORM.On("FindBridge", mock.Anything, name).Return(bridges.BridgeType{
					Name:                   name,
					URL:                    models.WebURL(*bridgeURL),
					Confirmations:          uint32(1),
					OutgoingToken:          "outgoingToken",
					MinimumContractPayment: assets.NewLinkFromJuels(1),
					CreatedAt:              f.Timestamp(),
				}, nil)
			},
			query: query,
			result: `{
				"bridge": {
					"id": "bridge1",
					"name": "bridge1",
					"url": "https://external.adapter",
					"confirmations": 1,
					"outgoingToken": "outgoingToken",
					"minimumContractPayment": "1",
					"createdAt": "2021-01-01T00:00:00Z"
				}
			}`,
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

**File:** core/cmd/bridge_commands.go (L52-78)
```go
// RenderTable implements TableRenderer
func (p *BridgePresenter) RenderTable(rt RendererTable) error {
	table := rt.newTable([]string{"Name", "URL", "Default Confirmations", "Outgoing Token"})
	table.Append([]string{
		p.Name,
		p.URL,
		p.FriendlyConfirmations(),
		p.OutgoingToken,
	})
	return render("Bridge", table)
}

type BridgePresenters []BridgePresenter

// RenderTable implements TableRenderer
func (ps BridgePresenters) RenderTable(rt RendererTable) error {
	table := rt.newTable([]string{"Name", "URL", "Confirmations"})
	for _, p := range ps {
		table.Append([]string{
			p.Name,
			p.URL,
			p.FriendlyConfirmations(),
		})
	}

	return render("Bridges", table)
}
```
