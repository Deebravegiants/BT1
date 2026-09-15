The claim is well-supported by the code. `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` are registered with no `auth.RequiresEditRole`/`auth.RequiresAdminRole` wrapper, unlike sibling routes such as `POST /v2/bridge_types`, `PATCH`, and `DELETE` [1](#0-0) . `OutgoingToken` is a genuine secret generated via `utils.NewSecret(24)` alongside `IncomingToken` at bridge-creation time [2](#0-1) , and it is persisted in plaintext on the `BridgeType` model (unlike `IncomingToken`, which is only stored as a hash) [3](#0-2) . `NewBridgeResource` unconditionally copies `b.OutgoingToken` into the JSON response with no `omitempty` tag, while `IncomingToken` is deliberately given `omitempty` and only populated at creation time [4](#0-3) . Both `Index` and `Show` build their responses through this same presenter with no redaction [5](#0-4) .

Audit Report

## Title
Bridge `OutgoingToken` secret is returned unmasked to any authenticated "view"-role user via the Bridge Types API - ([File: core/web/presenters/bridges.go])

## Summary
`GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` return the bridge's plaintext `OutgoingToken` to any authenticated user, including those with only the "view" role, because these routes lack the `auth.RequiresEditRole`/`auth.RequiresAdminRole` gating applied to write operations, and `BridgeResource.OutgoingToken` is serialized unconditionally with no `omitempty` or redaction.

## Finding Description
`NewBridgeType` generates both `IncomingToken` and `OutgoingToken` as 24-byte secrets when a bridge is created, but only `IncomingToken` is hashed before persistence (`IncomingTokenHash`); `OutgoingToken` is stored and kept in plaintext in the `bridges.BridgeType` model. `BridgeResource` in `core/web/presenters/bridges.go` marks `IncomingToken` with `json:"incomingToken,omitempty"` and only ever populates it from the one-time `BridgeTypeAuthentication` response returned by `Create`, but `OutgoingToken` has no `omitempty` tag and `NewBridgeResource` always sets `OutgoingToken: b.OutgoingToken` directly from the persisted model. `BridgeTypesController.Index` and `.Show` both call `presenters.NewBridgeResource(bridge)` unconditionally. Critically, in `core/web/router.go`, the GET routes for bridges (`/bridge_types` and `/bridge_types/:BridgeName`) are registered on the `authv2` group with only session/token authentication and no role-based wrapper, whereas the mutating routes (`POST`, `PATCH`, `DELETE`) are explicitly wrapped with `auth.RequiresEditRole`. This means any authenticated user — including one with only the minimal "view" role — can call these GET endpoints and receive the bridge's `OutgoingToken` in the response.

## Impact Explanation
`OutgoingToken` is a credential associated with the bridge/external-adapter relationship. Its disclosure to any authenticated low-privilege user constitutes secret exfiltration beyond the intended trust boundary (a "view" role should only need read access to non-sensitive metadata, not raw credentials), mapping to the "key/secret exfiltration" impact category. This is a confidentiality-only issue: it does not by itself enable unauthorized job runs or fund movement, but it exposes an authentication token that could be used to interact with the external adapter/bridge endpoint on the node's behalf.

## Likelihood Explanation
Exploitation requires no special access beyond a valid "view"-role authenticated session or API token — the lowest privilege tier in the system. A simple `GET /v2/bridge_types` or `GET /v2/bridge_types/:BridgeName` call reveals the token; no race conditions, timing, or additional exploitation steps are needed, making this trivially and repeatably reachable.

## Recommendation
Apply the same write-only/one-time-disclosure treatment to `OutgoingToken` as done for `IncomingToken`: add `omitempty` to the JSON tag, strip it from `Index`/`Show`/`Update` responses (only return it once, at `Create` time), and/or restrict retrieval of bridge tokens to `edit`/`admin` roles rather than the default authenticated/view tier used by the current GET routes.

## Proof of Concept
1. As an admin, `POST /v2/bridge_types` to create a bridge; note the response includes `outgoingToken` (expected, one-time disclosure).
2. Create a session/API token for a separate user with role `view` (`sessions.UserRoleView`).
3. As the `view` user, call `GET /v2/bridge_types/:BridgeName` (or `GET /v2/bridge_types`).
4. Observe the response body contains the plaintext `outgoingToken` field identical to the one issued at creation, confirming `NewBridgeResource` (`core/web/presenters/bridges.go` L29-41) serializes it unconditionally and the route (`core/web/router.go` L269-271) has no role gate beyond authentication.

### Citations

**File:** core/web/router.go (L268-273)
```go
		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
```

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
