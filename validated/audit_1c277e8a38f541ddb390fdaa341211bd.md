Based on my investigation, the most relevant analog to the Jenkins IFTTT Build Notifier issue (unencrypted secret stored and exposed on read) in this codebase is the Bridge `OutgoingToken` handling.

### Title
Bridge `OutgoingToken` secret is stored in plaintext and disclosed on every authenticated read, unlike `IncomingToken` - (File: `core/web/presenters/bridges.go`)

### Summary
Chainlink's Bridge feature stores an `OutgoingToken` used to authenticate outbound requests to external adapters. Unlike `IncomingToken` (which is deliberately redacted after creation), `OutgoingToken` is persisted in plaintext in the `bridges` DB table [1](#0-0)  and is returned in full on every `Index`/`Show` read of a bridge, not just at creation time [2](#0-1) .

### Finding Description
`BridgeResource`, the JSON:API presenter used for both listing and showing bridges, marks `IncomingToken` as `omitempty` and only populates it explicitly right after creation (`resource.IncomingToken = bta.IncomingToken`), while `OutgoingToken` has no such redaction and is always populated from the stored DB value: [3](#0-2) . This means every call to `GET /v2/bridge_types` (Index) or `GET /v2/bridge_types/:BridgeName` (Show) returns the plaintext `OutgoingToken` for every bridge configured on the node [4](#0-3) . This is directly analogous to the Jenkins IFTTT plugin bug class: a secret credential (Maker Channel Key / here, the bridge's outgoing auth token) is stored unencrypted in a config-like record and exposed to any actor who can read that record, rather than being write-only or properly redacted after initial issuance.

### Impact Explanation
The `OutgoingToken` is the credential Chainlink itself presents when calling out to an external bridge/adapter. Any authenticated caller able to invoke the bridge read endpoints can retrieve this token for every bridge on the node, which could allow forging or replaying requests to third-party adapters that trust this token, or leaking a credential that should only be known to the node and the adapter operator.

### Likelihood Explanation
I was not able to conclusively confirm the exact role gate for the `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` routes in `core/web/router.go` before running out of tool iterations — I could see the routes exist (5 matches in `router.go`) but could not verify whether GET is limited to Admin/Edit or accessible to the lowest-privilege `UserRoleView` (or run-only external-initiator sessions) session, unlike the `/v2/jobs` GET routes I confirmed have no explicit role wrapper [5](#0-4) . This uncertainty limits how confidently I can assert "unprivileged actor" reachability — if GET bridge routes require Admin/Edit role, this finding's severity/likelihood drops substantially since it would only affect already-privileged operators, not an unprivileged actor as the rules require.

### Recommendation
- Redact `OutgoingToken` from `BridgeResource` on `Index`/`Show` responses, showing it only once at creation (mirroring `IncomingToken`'s `omitempty` treatment) or masking it (e.g., last 4 characters only).
- Confirm and, if necessary, restrict the `GET /v2/bridge_types*` routes in `core/web/router.go` to roles that legitimately need to manage/administer bridges rather than any authenticated read-level session.
- Consider storing `OutgoingToken` hashed/encrypted at rest, similar to how `IncomingTokenHash`/`Salt` are already handled for the incoming token [1](#0-0) .

### Proof of Concept
1. As any authenticated node user/session capable of reaching bridge read endpoints, call `GET /v2/bridge_types` or `GET /v2/bridge_types/{name}`.
2. Observe the JSON:API response includes `outgoingToken` in plaintext for the bridge, as confirmed by the existing test fixture [6](#0-5) .
3. Use the retrieved `outgoingToken` to impersonate the node when calling the associated external adapter, if the adapter trusts this token for authentication.

**Caveat:** This finding's classification as a valid unprivileged-actor analog depends on confirming the actual role requirement for these GET routes, which I could not fully verify within available tool calls — a background Devin session with full file access to `core/web/router.go` would be needed to confirm the exact `auth.RequiresXRole` wrapper (if any) applied to the bridge_types GET handlers before treating this as a confirmed, exploitable-by-unprivileged-actor vulnerability.

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

**File:** core/web/router.go (L391-396)
```go
		jc := JobsController{app}
		authv2.GET("/jobs", paginatedRequest(jc.Index))
		authv2.GET("/jobs/:ID", jc.Show)
		authv2.POST("/jobs", auth.RequiresEditRole(jc.Create))
		authv2.PUT("/jobs/:ID", auth.RequiresEditRole(jc.Update))
		authv2.DELETE("/jobs/:ID", auth.RequiresEditRole(jc.Delete))
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
