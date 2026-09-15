### Title
Bridge `OutgoingToken` secret is permanently exposed via read endpoints to any authenticated viewer - (File: `core/web/presenters/bridges.go`)

### Summary
Chainlink bridge types store an `OutgoingToken` secret (used to authenticate the node's outbound calls to an external adapter) in the `bridge_types` table. Unlike the `IncomingToken`, which is deliberately marshalled with `omitempty` and only populated transiently at creation time, the `OutgoingToken` field has no such guard and is unconditionally serialized on every read of a bridge resource (list, show, update, delete responses, and the GraphQL `Bridge` type). This is analogous to CVE-2016-6658's root cause: a credential associated with an externally-reachable URL is persisted and later disclosed to any party with read access, rather than being write-only/redacted after initial provisioning.

### Finding Description
`BridgeType.OutgoingToken` is stored in plaintext in the DB [1](#0-0) , and `NewBridgeResource` copies it into the JSON:API response unconditionally: [2](#0-1) . Compare this to `IncomingToken`, which is `json:"incomingToken,omitempty"` and is only ever set explicitly by `BridgeTypesController.Create` right after generation [3](#0-2) .

Because `OutgoingToken` has no `omitempty`/redaction, `Index`, `Show`, `Update`, and `Destroy` handlers in `BridgeTypesController` all return it in full on every call: [4](#0-3) [5](#0-4) [6](#0-5) . This is confirmed by the existing test which asserts `outgoingToken` appears in the JSON on list/show responses, without ever removing it from output: [7](#0-6) . The GraphQL schema mirrors this: the `Bridge` type always exposes `outgoingToken: String!` with no field-level access restriction distinct from other read-only bridge fields [8](#0-7) .

The `OutgoingToken` is meant to let an external adapter/bridge verify that a request actually originated from the Chainlink node. Anyone who can read this token can forge that verification for the corresponding external adapter — i.e., impersonate the node when calling the bridge's callback path — which is exactly the risk class described in CVE-2016-6658 (credential embedded/tied to a URL, persisted, later readable by parties who shouldn't retain long-term access to it).

### Impact Explanation
Any actor who is able to invoke the bridge read endpoints (`GET /v2/bridge_types`, `GET /v2/bridge_types/:name`, or the equivalent GraphQL `bridge`/`bridges` queries) obtains the live `OutgoingToken` for every configured bridge, not just the one they created. This token can be replayed to impersonate the Chainlink node's outbound calls to the corresponding external adapter, a form of request/identity impersonation. I could not fully verify from the available index which specific role tier (`view`/`run`/`edit`/`admin`) chainlink's router assigns to these particular routes — that check happens in `core/web/router.go`'s route-group middleware, and I was unable to pull the exact role-to-route mapping lines for `bridge_types` before the tool budget ran out. If a lower-privilege "view-only" role (which exists in Chainlink's role model for read access) is sufficient to hit these GET endpoints, this is a clear least-privilege violation and secret-disclosure bug; if only `admin`/`edit` roles can reach them, the impact is reduced to unnecessary secret retention rather than a privilege boundary bypass. Given this uncertainty, I flag it as a probable but not fully confirmed cross-role disclosure.

### Likelihood Explanation
Likelihood is high for any authenticated user who can call the bridge listing/show endpoints at all, since no additional secret-specific guard exists — the exposure happens on the normal, expected read path, not through any exotic exploit chain.

### Recommendation
Add `omitempty`-style redaction (or drop the field from `BridgeResource` entirely on read responses) so `OutgoingToken` is returned only once, at creation time, exactly as `IncomingToken` already is. If the outgoing token must be re-displayed for legitimate re-configuration flows, gate that behind an explicit "reveal" action restricted to the `admin`/`edit` role rather than the default read path, and rotate/hash it so raw disclosure isn't required for verification.

### Proof of Concept
1. Create a bridge as an authorized user: `POST /v2/bridge_types` → response includes a fresh `outgoingToken`.
2. As any other actor able to reach `GET /v2/bridge_types` or `GET /v2/bridge_types/:name` (or the GraphQL `bridges`/`bridge` query), observe that the same `outgoingToken` value is returned in the JSON body, confirmed by the presenter behavior in [9](#0-8)  and its corresponding test fixture [7](#0-6) .
3. Use the retrieved `outgoingToken` to impersonate node-to-adapter callback verification for that bridge's external adapter endpoint.

**Note:** I was not able to conclusively determine the exact role/permission required to invoke the bridge read endpoints from the indexed portion of `core/web/router.go` before running out of tool calls — this is the key remaining gap for fully confirming an "unprivileged-actor" bypass versus an over-broad-but-still-privileged disclosure. If a Devin session with full repo access is available, I'd recommend directly inspecting `core/web/router.go`'s `v2Routes`/bridge routes group and the role-check middleware (e.g., `authenticatedRateLimiter`, `RequiresAuth`, or per-route `Use(auth...)` calls) to confirm the minimum role able to reach `GET /v2/bridge_types*`.

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

**File:** core/web/bridge_types_controller.go (L98-99)
```go
	resource := presenters.NewBridgeResource(*bt)
	resource.IncomingToken = bta.IncomingToken
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

**File:** core/web/bridge_types_controller.go (L184-192)
```go
	btc.App.GetAuditLogger().Audit(audit.BridgeUpdated, map[string]any{
		"bridgeName":                   bt.Name,
		"bridgeConfirmations":          bt.Confirmations,
		"bridgeMinimumContractPayment": bt.MinimumContractPayment,
		"bridgeURL":                    bt.URL,
	})

	jsonAPIResponse(c, presenters.NewBridgeResource(bt), "bridge")
}
```

**File:** core/web/bridge_types_controller.go (L224-232)
```go
	if err = orm.DeleteBridgeType(ctx, &bt); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, fmt.Errorf("failed to delete bridge: %w", err))
		return
	}

	btc.App.GetAuditLogger().Audit(audit.BridgeDeleted, map[string]any{"name": name})

	jsonAPIResponse(c, presenters.NewBridgeResource(bt), "bridge")
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

**File:** deployment/environment/web/sdk/internal/schema.graphql (L118-126)
```text
type Bridge {
    id: ID!
    name: String!
    url: String!
    confirmations: Int!
    outgoingToken: String!
    minimumContractPayment: String!
    createdAt: Time!
}
```
