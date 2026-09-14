### Title
Bridge job configuration API discloses unmasked `OutgoingToken` credential to any authenticated node user via `Index`/`Show` - ([File: core/web/presenters/bridges.go])

### Summary
The Jenkins DiveCloud advisory describes a job configuration form that displays API keys/credential encryption keys in plaintext instead of masking them, letting any user who can view the job config observe long‑lived secrets. The chainlink node has a direct analog in the Bridge (External Adapter) configuration API: the `OutgoingToken` credential is returned unmasked in every bridge read response (`Index`, `Show`, `Update`, `Destroy`), not only at creation time as intended.

### Finding Description
`BridgeResource` is the JSON:API presenter used for all bridge endpoints. Its `OutgoingToken` field has no `omitempty` and is unconditionally populated from the stored `BridgeType.OutgoingToken` value: [1](#0-0) 

`NewBridgeResource` always copies `b.OutgoingToken` into the resource regardless of which controller action produced it: [2](#0-1) 

The comment on `IncomingToken` ("only provided when creating a Bridge") signals developer intent that secrets should be creation-only/one-time-reveal, matching the `IncomingToken`'s `omitempty` handling in `BridgeTypesController.Create`, which explicitly sets it only in that one path: [3](#0-2) 

However, no equivalent protection exists for `OutgoingToken`. `BridgeTypesController.Index` and `.Show` — reachable by any authenticated node user with only read access — build the resource straight from stored `BridgeType` and return it as-is, leaking the plaintext `OutgoingToken` on every listing/view: [4](#0-3) 

The same unmasked value is also returned on `Update` and `Destroy` responses: [5](#0-4) 

This mirrors the Jenkins bug class exactly: a credential intended to be secret is displayed in the job/bridge configuration view instead of being masked, increasing the risk that it is captured by an observer (screen share, browser history, proxy/log capture, shared session, or a lower-privileged viewer role if one exists).

### Impact Explanation
`OutgoingToken` is a bearer-style credential used to authenticate bridge (external adapter) callback requests. Disclosure through the bridge listing/detail API lets any actor who can reach these read endpoints obtain a long-lived secret that can be used to impersonate the node when interacting with the external adapter, or to replay/interfere with bridge responses. This is a genuine secret-disclosure (CWE-256-class) issue reachable from a standard, non-admin read endpoint.

### Likelihood Explanation
High for any user who already has API access to the node's bridge routes (`GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`). No special exploitation is required — the secret is returned in the normal JSON response body of routine, expected API calls.

### Recommendation
Do not include `OutgoingToken` in `BridgeResource` for read paths (`Index`/`Show`/`Update`/`Destroy`); treat it the same way as `IncomingToken` — reveal only once at creation (or never over the read API), and mask/redact it (e.g., `omitempty` + only set at creation, or return a redacted placeholder) for all subsequent reads.

### Proof of Concept
1. Create a bridge: `POST /v2/bridge_types` with a valid session — response includes both `incomingToken` and `outgoingToken` in plaintext (expected, one-time).
2. As any authenticated node user, call `GET /v2/bridge_types` or `GET /v2/bridge_types/{name}` — observe that `outgoingToken` is still returned in plaintext in the JSON:API response body, via `NewBridgeResource` populating it unconditionally as shown in `core/web/presenters/bridges.go:37`.

### Citations

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

**File:** core/web/bridge_types_controller.go (L149-232)
```go
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

// Destroy removes a specific Bridge.
func (btc *BridgeTypesController) Destroy(c *gin.Context) {
	ctx := c.Request.Context()
	name := c.Param("BridgeName")

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
		jsonAPIError(c, http.StatusInternalServerError, fmt.Errorf("error searching for bridge: %w", err))
		return
	}
	jobsUsingBridge, err := btc.App.JobORM().FindJobIDsWithBridge(ctx, name)
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, fmt.Errorf("error searching for associated v2 jobs: %w", err))
		return
	}
	if len(jobsUsingBridge) > 0 {
		jsonAPIError(c, http.StatusConflict, fmt.Errorf("can't remove the bridge because jobs %v are associated with it", jobsUsingBridge))
		return
	}
	if err = orm.DeleteBridgeType(ctx, &bt); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, fmt.Errorf("failed to delete bridge: %w", err))
		return
	}

	btc.App.GetAuditLogger().Audit(audit.BridgeDeleted, map[string]any{"name": name})

	jsonAPIResponse(c, presenters.NewBridgeResource(bt), "bridge")
}
```
