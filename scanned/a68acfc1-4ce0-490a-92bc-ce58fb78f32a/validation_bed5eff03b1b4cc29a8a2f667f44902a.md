### Title
Unauthenticated-role bypass exposing plaintext Bridge `OutgoingToken` via unrestricted `GET /v2/bridge_types/:BridgeName` - ([File: core/web/router.go])

### Summary
The `chainlink--001` node stores a bridge's `OutgoingToken` (the credential the node sends to the external adapter) unencrypted in the `bridge_type` DB row and exposes it verbatim in the API's `BridgeResource` presenter. Unlike `Create`, `Update`, and `Destroy`, the `Show` route for this endpoint has no role-gating middleware, so any authenticated user — including the lowest-privilege `view` role — can retrieve this plaintext credential. This mirrors the QMetry-for-Jira bug class (CWE-522: credentials stored/exposed in plaintext, accessible to lower-privileged/extended users) but manifests here as a role-check omission rather than a config.xml leak.

### Finding Description
`BridgeType.OutgoingToken` is stored in plaintext in the DB (only `IncomingToken` is hashed/salted): [1](#0-0) 

The presenter unconditionally serializes this token to API responses: [2](#0-1) 

`BridgeTypesController.Show` fetches the bridge and returns it via `presenters.NewBridgeResource(bt)` with no redaction: [3](#0-2) 

Critically, in the router, the mutating bridge routes are wrapped in `auth.RequiresEditRole`, but `Show` is registered bare: [4](#0-3) 

```go
authv2.GET("/bridge_types", paginatedRequest(bt.Index))
authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
authv2.GET("/bridge_types/:BridgeName", bt.Show)
authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
```

`Show` and `Index` only pass through the generic `Authenticate` middleware (session or API token), with no `RequiresEditRole`/`RequiresRunRole`/`RequiresAdminRole` check: [5](#0-4) 

The role hierarchy defined in `core/sessions/user.go` explicitly includes a `view`-only role intended to be the least privileged tier: [6](#0-5) 

`RequiresRunRole` and `RequiresEditRole` both explicitly block `UserRoleView` from run/edit-gated endpoints: [7](#0-6) 

But because `Show`/`Index` bypass these checks entirely, a `view`-role user (the analog of Jenkins' "Extended Read permission" user in the referenced advisory) can call `GET /v2/bridge_types/:BridgeName` and receive the bridge's plaintext `OutgoingToken` — a secret meant to authenticate the node to an external adapter.

### Impact Explanation
The `OutgoingToken` is a bearer credential used by the Chainlink node to authenticate itself to external bridge adapters. A `view`-role user is intended only to observe node state, not to obtain secrets that allow acting as the node toward external systems. Exposure of this token allows a low-privileged, non-editor user to impersonate the node's outbound calls to the external adapter, or to exfiltrate a credential that should be restricted to edit/admin-level operators. This satisfies the "concrete ... key/secret disclosure" acceptance criterion via a role-check bypass in the internet-facing API surface, not a mocked or operator-only path.

### Likelihood Explanation
Likelihood is moderate-to-high in any deployment that provisions `view`-role API users (a supported, intended low-trust tier per `core/sessions/user.go`) alongside bridges holding secrets. The request requires only a valid authenticated session/API token of any role — no edit/run/admin privilege, and no additional exploitation complexity; it's a single unauthenticated-role GET request against a documented REST route.

### Recommendation
Wrap `authv2.GET("/bridge_types/:BridgeName", bt.Show)` (and ideally the `Index` route) with `auth.RequiresEditRole` (or a new intermediate role check) so that only users authorized to manage bridges can view the `OutgoingToken`. Alternatively, redact/omit `OutgoingToken` from `BridgeResource` for callers below `edit` role, mirroring how `IncomingToken` is already only returned at creation time (`omitempty` field) in `core/web/presenters/bridges.go`.

### Proof of Concept
1. Provision a Chainlink node user with `UserRoleView` (e.g., via `admin users create` with role `view`).
2. As an admin, create a bridge: `POST /v2/bridge_types` → note that `OutgoingToken` is generated and persisted in plaintext (`core/bridges/bridge_type.go` `NewBridgeType`).
3. Authenticate as the `view`-role user (session cookie or API token).
4. Call `GET /v2/bridge_types/<bridgeName>` as this view user.
5. Observe the response includes the plaintext `outgoingToken` field (per `BridgeResource.OutgoingToken` in `core/web/presenters/bridges.go`), despite the user having only view privileges — confirmed by the absence of any `RequiresEditRole`/`RequiresRunRole` wrapper on this route in `core/web/router.go` line 271, in contrast to the adjacent `Create`/`Update`/`Destroy` routes.

### Citations

**File:** core/bridges/bridge_type.go (L44-68)
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

**File:** core/web/router.go (L245-248)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
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

**File:** core/sessions/user.go (L27-34)
```go
type UserRole string

const (
	UserRoleAdmin UserRole = "admin"
	UserRoleEdit  UserRole = "edit"
	UserRoleRun   UserRole = "run"
	UserRoleView  UserRole = "view"
)
```

**File:** core/web/auth/auth.go (L198-234)
```go
// RequiresRunRole extracts the user object from the context, and asserts the user's role is at least
// 'run'
func RequiresRunRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}

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
