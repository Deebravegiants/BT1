Audit Report

## Title
Bridge `OutgoingToken` credential disclosed to any authenticated `View`-role user via `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` - (File: core/web/router.go)

## Summary
The Chainlink node's multi-user RBAC system defines four roles (`admin`, `edit`, `run`, `view`), with `view` intended as read-only, minimal-privilege access. The bridge type read routes (`Index`/`Show`) are registered without any `auth.RequiresEditRole`/`auth.RequiresAdminRole` wrapper, while the mutating routes on the same resource (`Create`, `Update`, `Destroy`) are correctly gated with `auth.RequiresEditRole`. Both read handlers return `presenters.BridgeResource`, which unconditionally serializes the plaintext `OutgoingToken` secret, so a `UserRoleView` account can retrieve every bridge's outbound authentication secret.

## Finding Description
Route registration in `v2Routes`: [1](#0-0) 

confirms `GET /bridge_types` and `GET /bridge_types/:BridgeName` carry only the base session/token `Authenticate` middleware from the `authv2` group, with no role check, whereas the immediately adjacent `POST`/`PATCH`/`DELETE` handlers are wrapped in `auth.RequiresEditRole`.

The role hierarchy is real and enforced elsewhere: `UserRoleAdmin`, `UserRoleEdit`, `UserRoleRun`, `UserRoleView` are defined in `core/sessions/user.go`, and `auth.RequiresEditRole` explicitly rejects `UserRoleView` and `UserRoleRun`: [2](#0-1) 

This shows the codebase's own security model treats `view` as strictly lower-privileged than `edit`/`admin`, and this distinction is applied consistently to the write endpoints of the same `bridge_types` resource but omitted from the read endpoints — a clear inconsistency, not an intentional design (list/detail views of other sensitive resources, e.g. `/users`, are correctly gated with `RequiresAdminRole`).

`Index` and `Show` both return `presenters.BridgeResource`, which serializes `OutgoingToken` unconditionally (unlike `IncomingToken`, which is `omitempty` and populated only on creation): [3](#0-2) [4](#0-3) [5](#0-4) 

`OutgoingToken` is a real secret generated at bridge creation (`utils.NewSecret(24)`) used by the node to authenticate outbound calls to the external adapter: [6](#0-5) 

Exploit flow: an operator provisions a low-privilege account with `UserRoleView` (the intended minimal, read-only role, obtainable via `POST /v2/users` by an admin, or via LDAP/OIDC "read" group mapping as seen in `core/sessions/ldapauth/ldap.go` and `core/sessions/oidcauth/oidc.go`). That `view`-role user authenticates normally (session cookie or API token) and issues `GET /v2/bridge_types` or `GET /v2/bridge_types/:BridgeName`. Because no role check exists on these routes, the request succeeds and the response includes `outgoingToken` in plaintext for every bridge, identical to what an `admin` would see.

## Impact Explanation
`OutgoingToken` is a credential the node uses to authenticate itself to external adapters. Disclosure to a `view`-role principal — who is only supposed to have read visibility, not secrets or write access — breaks the intended privilege boundary between `view` and `edit`/`admin` roles, and gives that principal the ability to impersonate the node's outbound calls to the configured bridge endpoint. This is a concrete secret-disclosure / role-bypass issue localized to the node's own API authorization logic (not a leaked-credential or misconfiguration scenario), matching the "node API authentication or role bypass" / "key or secret exfiltration" impact classes.

## Likelihood Explanation
High for anyone who already holds (or is granted) a `view`-role account or API token — which is by design the lowest, most freely provisioned tier (e.g., LDAP/OIDC read-group mapping automatically assigns `UserRoleView`). No CSRF token, elevated role, or extra confirmation is required, unlike other sensitive endpoints (e.g., `NewAPIToken`, which re-verifies password). The request is a simple authenticated `GET`, fully reproducible and repeatable.

## Recommendation
Wrap `authv2.GET("/bridge_types", ...)` and `authv2.GET("/bridge_types/:BridgeName", ...)` in `core/web/router.go` with `auth.RequiresEditRole` (consistent with the write handlers on the same resource), or alternatively strip `OutgoingToken` from `BridgeResource` for list/show responses (mirroring the existing `omitempty`/create-only treatment of `IncomingToken` in `core/web/presenters/bridges.go`), exposing it only at creation time or behind an admin-only endpoint.

## Proof of Concept
1. As an admin, create a bridge: `POST /v2/bridge_types` with `{"name":"test-bridge","url":"https://adapter.example.com"}`, which generates and stores an `OutgoingToken` (`core/bridges/bridge_type.go` `NewBridgeType`).
2. As an admin, create a `view`-role user: `POST /v2/users` with role `view` (per `core/web/user_controller.go` and `core/sessions/user.go` `UserRoleView`), or authenticate via LDAP/OIDC into a group mapped to the read/view role.
3. Authenticate as that `view`-role user (session cookie via `/sessions` or API token).
4. Issue `GET /v2/bridge_types/test-bridge` (or `GET /v2/bridge_types`) using only that session/token — no `RequiresEditRole`/`RequiresAdminRole` check exists on this route (`core/web/router.go` lines 268-273).
5. Observe the JSON response body includes `"outgoingToken": "<plaintext secret>"`, identical to the admin-visible value, confirming disclosure to a low-privilege role.
6. As a regression/verification test, add a handler test in `core/web/bridge_types_controller_test.go` asserting that a `view`-role authenticated client is rejected (`401`/`403`) on `Index`/`Show`, matching the existing role-check tests already present for other `RequiresEditRole`-gated bridge operations.

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

**File:** core/web/auth/auth.go (L217-234)
```go
// RequiresEditRole extracts the user object from the context, and asserts the user's role is at least
// 'edit'
func RequiresEditRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView || user.Role == clsessions.UserRoleRun {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}
```

**File:** core/web/presenters/bridges.go (L10-42)
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
}
```

**File:** core/web/bridge_types_controller.go (L112-122)
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
```

**File:** core/web/bridge_types_controller.go (L124-146)
```go
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

**File:** core/bridges/bridge_type.go (L55-102)
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
}
```
