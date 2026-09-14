### Title
Bridge Outgoing Token Secret Disclosure via `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` - (File: core/web/presenters/bridges.go)

### Summary
Chainlink's `BridgeResource` JSONAPI presenter unconditionally serializes the bridge's `OutgoingToken` secret in every response, and the `GET /v2/bridge_types` (Index) and `GET /v2/bridge_types/:BridgeName` (Show) routes are reachable by any authenticated user without any role check, unlike the `Create`/`Update`/`Destroy` routes which require `RequiresEditRole`. This mirrors the Onyx analog: an admin-configured secret meant for third-party/external-adapter authentication is disclosed in plaintext to any authenticated caller who can reach a read-only "get resource" endpoint.

### Finding Description
The bridge type's `OutgoingToken` is a secret credential generated at bridge creation time (alongside `IncomingToken`, `IncomingTokenHash`, and `Salt`) intended to authenticate outbound calls from the node to the External Adapter / callback consumer [1](#0-0) .

The `BridgeResource` presenter includes this token in every serialized response with no redaction and no `omitempty` gate (unlike `IncomingToken`, which is explicitly commented as "only provided when creating a Bridge" and marked `omitempty`): [2](#0-1) 

Both the `Index` and `Show` handlers build this resource directly from the DB row and return it as-is: [3](#0-2) 

Critically, in the route table, the mutating bridge endpoints (`POST`, `PATCH`, `DELETE`) are wrapped with `auth.RequiresEditRole`, but the two read endpoints are not gated by any role check at all — they only require successful authentication (session cookie or API token): [4](#0-3) 

This means any authenticated user — including a low-privilege `View` role user who only has read access — can call `GET /v2/bridge_types` or `GET /v2/bridge_types/:BridgeName` and receive every bridge's `OutgoingToken` in plaintext, directly analogous to the Onyx bug where `GET /tool/{tool_id}` leaked admin-configured `custom_headers` credentials to any authenticated user.

### Impact Explanation
`OutgoingToken` is a secret used to authenticate outbound requests to the configured bridge/External Adapter URL. Disclosure of this token to an unprivileged, authenticated user allows that user to directly interact with the third-party/external adapter endpoint using the node's authorized credentials, impersonating the node or accessing upstream systems the low-privilege user should never have access to. This satisfies the "concrete secret disclosure" bar from the analog rules — an admin-defined credential is exposed via a GET endpoint reachable by any authenticated, non-privileged actor.

### Likelihood Explanation
High likelihood of reachability: any user who can authenticate (via session or a low-privilege API token) and knows or enumerates bridge names can trivially call the unguarded `GET` routes. No additional exploit primitives are required — this is a direct, single-request information disclosure once a node has any bridges configured, which is a near-universal deployment pattern (bridges back most Chainlink jobs).

### Recommendation
- Redact `OutgoingToken` from `BridgeResource` on read paths (`Index`/`Show`), keeping it `omitempty` and only populated on `Create` (and possibly `Update`), mirroring how `IncomingToken` is already handled.
- Alternatively/additionally, gate `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` behind `auth.RequiresEditRole` (or a role capable of viewing secrets) so read-only/`View` role users cannot retrieve the secret at all.

### Proof of Concept
1. As an admin, create a bridge: `POST /v2/bridge_types/` with `{"name":"mybridge","url":"http://adapter.example"}` — response includes `outgoingToken`.
2. As a lower-privileged authenticated user (`View` role, or any user/API token that only needs to authenticate, since no role check is applied on the GET routes), call:
   - `GET /v2/bridge_types/mybridge` — response body includes the plaintext `outgoingToken` field (see `presenters.BridgeResource` at [5](#0-4) ).
   - `GET /v2/bridge_types` — same disclosure for every configured bridge.
3. Use the disclosed `outgoingToken` to authenticate requests directly to the external adapter/bridge URL configured for that bridge.

Note: I was not able to fully verify from the index how `OutgoingToken` is consumed on the outbound call path (e.g., whether it's sent as a header to the External Adapter) due to index size limits on some files; a Devin session with full repo access could confirm the exact usage site to strengthen the impact analysis.

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
