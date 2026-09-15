All claims in the report are verified directly against the code.

Audit Report

## Title
Bridge Outgoing Authentication Token Disclosed to Read-Only Users via GET /v2/bridge_types - (File: core/web/bridge_types_controller.go)

## Summary
`GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, and the GraphQL `bridges`/`bridge` queries are reachable by any authenticated user regardless of role, including the lowest-privilege `view` role. The response serializer unconditionally includes each bridge's `OutgoingToken`, a plaintext secret used to authenticate the node to external adapters, with no redaction and no elevated role check.

## Finding Description
`authv2.GET("/bridge_types", ...)` and `authv2.GET("/bridge_types/:BridgeName", ...)` are registered under the generic authenticated group with no `auth.RequiresEditRole`/`RequiresAdminRole` wrapper, unlike the sibling `POST`/`PATCH`/`DELETE` bridge routes which explicitly require edit role: [1](#0-0) 

`BridgeTypesController.Index` and `Show` fetch bridges from the ORM and pass them directly to `presenters.NewBridgeResource` with no field filtering: [2](#0-1) 

`BridgeResource.OutgoingToken` is a plain (non-`omitempty`) JSON field, unlike `IncomingToken` which is `omitempty` and only populated by the `Create` handler at bridge-creation time: [3](#0-2)  `NewBridgeResource` copies `b.OutgoingToken` straight from the DB-backed `bridges.BridgeType` into the presenter with no redaction: [4](#0-3) 

The `OutgoingToken` is generated as a real plaintext secret alongside the (hashed) `IncomingToken` and persisted in plaintext in `BridgeType.OutgoingToken`: [5](#0-4) 

On the GraphQL side, `Resolver.Bridge` and `Resolver.Bridges` both call `authenticateUser(ctx)`, which only checks that a valid session exists — it does not check role level at all, unlike `authenticateUserCanEdit`/`authenticateUserIsAdmin`: [6](#0-5) [7](#0-6)  The `BridgeResolver.OutgoingToken()` method then returns the raw token unconditionally: [8](#0-7) 

This confirms the reported root cause: read routes/queries are authenticated but not role-gated to match their mutation siblings, and the presenter/resolver perform no redaction of the `OutgoingToken` secret field.

## Impact Explanation
`OutgoingToken` is the credential the node uses to authenticate outbound calls to the external adapter/bridge endpoint. Any authenticated user — even one restricted to the `view` role, which is intended to be read-only and non-privileged — can retrieve this secret via `GET /v2/bridge_types` or the GraphQL `bridges`/`bridge` query. This lets a low-privilege user impersonate the node against the external adapter or otherwise interact with the downstream bridge/EA infrastructure that the token is meant to protect, a legitimate secret-disclosure impact affecting the confidentiality of a connected downstream system.

## Likelihood Explanation
This is trivially reachable: any authenticated session (any role) can call the existing, unmodified route/query and always receives the token whenever any bridge exists — no race conditions, timing, or special configuration required. This is a realistic and repeatable path for any deployment that grants `view`-role access to less-trusted users, which is a documented, intended use of that role.

## Recommendation
- Redact `OutgoingToken` from `presenters.BridgeResource` in `Index`/`Show`/`Update`/`Destroy` responses, mirroring how `IncomingToken` is `omitempty` and populated only in `Create`.
- Alternatively/additionally, require `auth.RequiresEditRole` or `auth.RequiresAdminRole` on `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` in `core/web/router.go`.
- Apply an equivalent role gate (`authenticateUserCanEdit`/`authenticateUserIsAdmin`) in the GraphQL `Bridge`/`Bridges` resolvers in `core/web/resolver/query.go`, or redact `OutgoingToken` in `BridgeResolver.OutgoingToken()`.

## Proof of Concept
1. Create/obtain a session or API token for a user with `sessions.UserRoleView`.
2. As that user, issue `GET /v2/bridge_types` (or `GET /v2/bridge_types/:BridgeName`) against a node with at least one configured bridge.
3. Observe the JSON response includes `attributes.outgoingToken` containing the plaintext secret, as confirmed by the existing test fixture asserting this exact field: [9](#0-8) 
4. Equivalently, run the GraphQL query `{ bridges { results { outgoingToken } } }` as a `view`-role session; `authenticateUser` only checks session presence, not role, so the query succeeds and returns the token, matching the existing test expectation: [10](#0-9)

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

**File:** core/web/presenters/bridges.go (L29-42)
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
}
```

**File:** core/bridges/bridge_type.go (L44-101)
```go
// BridgeTypeAuthentication is the record returned in response to a request to create a BridgeType
type BridgeTypeAuthentication struct {
	Name                   BridgeName
	URL                    models.WebURL
	Confirmations          uint32
	IncomingToken          string
	OutgoingToken          string
	MinimumContractPayment *assets.Link
	UseConnectionManager   bool `json:"useConnectionManager"`
}

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

**File:** core/web/resolver/query.go (L27-60)
```go
// Bridge retrieves a bridges by name.
func (r *Resolver) Bridge(ctx context.Context, args struct{ ID graphql.ID }) (*BridgePayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}

	name, err := bridges.ParseBridgeName(string(args.ID))
	if err != nil {
		return nil, err
	}

	bridge, err := r.App.BridgeORM().FindBridge(ctx, name)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return NewBridgePayload(bridge, err), nil
		}

		return nil, err
	}

	return NewBridgePayload(bridge, nil), nil
}

// Bridges retrieves a paginated list of bridges.
func (r *Resolver) Bridges(ctx context.Context, args struct {
	Offset *int32
	Limit  *int32
}) (*BridgesPayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}

	offset := pageOffset(args.Offset)
	limit := pageLimit(args.Limit)
```

**File:** core/web/resolver/auth.go (L11-43)
```go
// Authenticates the user from the session cookie, presence of user inherently provides 'view' access.
func authenticateUser(ctx context.Context) error {
	if _, ok := auth.GetGQLAuthenticatedSession(ctx); !ok {
		return unauthorizedError{}
	}
	return nil
}

// Authenticates the user from the session cookie and asserts at least 'run' role.
func authenticateUserCanRun(ctx context.Context) error {
	session, ok := auth.GetGQLAuthenticatedSession(ctx)
	if !ok {
		return unauthorizedError{}
	}
	if session.User.Role == sessions.UserRoleView {
		return RoleNotPermittedError{session.User.Role}
	}
	return nil
}

// Authenticates the user from the session cookie and asserts at least 'edit' role.
func authenticateUserCanEdit(ctx context.Context) error {
	session, ok := auth.GetGQLAuthenticatedSession(ctx)
	if !ok {
		return unauthorizedError{}
	}
	switch session.User.Role {
	case sessions.UserRoleView, sessions.UserRoleRun:
		return RoleNotPermittedError{session.User.Role}
	default:
	}
	return nil
}
```

**File:** core/web/resolver/bridge.go (L52-55)
```go
// OutgoingToken resolves the bridge's outgoing token.
func (r *BridgeResolver) OutgoingToken() string {
	return r.bridge.OutgoingToken
}
```

**File:** core/web/presenters/bridges_test.go (L39-54)
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
```

**File:** core/web/resolver/bridge_test.go (L63-79)
```go
			result: `
			{
				"bridges": {
					"results": [{
						"id": "bridge1",
						"name": "bridge1",
						"url": "https://external.adapter",
						"confirmations": 1,
						"outgoingToken": "outgoingToken",
						"minimumContractPayment": "1",
						"createdAt": "2021-01-01T00:00:00Z"
					}],
					"metadata": {
						"total": 1
					}
				}
			}`,
```
