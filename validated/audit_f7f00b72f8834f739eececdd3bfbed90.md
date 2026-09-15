All findings in the claim are confirmed by the actual code: the router only wraps `Create`/`Update`/`Destroy` with `auth.RequiresEditRole`, while `Index` and `Show` are reachable by any authenticated user regardless of role. [1](#0-0) 
The `Show` handler returns the bridge via `presenters.NewBridgeResource`, which unconditionally populates `OutgoingToken` from the DB-stored plaintext field. [2](#0-1) [3](#0-2) [4](#0-3) 
The role model confirms `RequiresEditRole` blocks `UserRoleView`/`UserRoleRun` but the plain `Authenticate` middleware admits any successfully authenticated user (session or API token) of any role, so a `ReadOnly`(view)/`Run` role user passes through to `Show` unimpeded. [5](#0-4) 

Audit Report

## Title
Any authenticated node role (including ReadOnly/Run) can retrieve a Bridge's plaintext OutgoingToken via `GET /v2/bridge_types/:BridgeName` - (File: core/web/router.go)

## Summary
The `/v2/bridge_types/:BridgeName` `Show` route is only gated by session/token authentication (`auth.Authenticate`), with no `auth.RequiresEditRole`/`RequiresAdminRole` check, unlike the sibling `Create`, `Update`, and `Destroy` routes on the same resource. The `Show` handler returns `presenters.NewBridgeResource(bt)`, which always serializes the bridge's `OutgoingToken` in plaintext, exposing a sensitive credential to any authenticated user regardless of role, including `View`/`Run`.

## Finding Description
In `core/web/router.go`, the bridge routes are:
```go
bt := BridgeTypesController{app}
authv2.GET("/bridge_types", paginatedRequest(bt.Index))
authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
authv2.GET("/bridge_types/:BridgeName", bt.Show)
authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
```
Only `Create`, `Update`, `Destroy` are wrapped with `RequiresEditRole`; `Index` and `Show` inherit only the base `authv2` group authentication (session or API token), with no role check at all. `RequiresEditRole` explicitly blocks `UserRoleView` and `UserRoleRun`, confirming those roles are intended to be excluded from mutation but are not excluded from `Show`/`Index`.

`BridgeTypesController.Show` fetches the bridge and serializes it without any field redaction or role check:
```go
bt, err := btc.App.BridgeORM().FindBridge(ctx, taskType)
...
jsonAPIResponse(c, presenters.NewBridgeResource(bt), "bridge")
```
`presenters.NewBridgeResource` unconditionally sets `OutgoingToken: b.OutgoingToken` on the response struct, whose JSON tag has no `omitempty`, unlike `IncomingToken` (`json:"incomingToken,omitempty"`), which is only populated at creation time and never stored/read back in plaintext (the DB stores only `IncomingTokenHash` + `Salt`). By contrast, `bridges.BridgeType.OutgoingToken` is stored in plaintext in the `outgoing_token` DB column and returned verbatim on every `Show`/`Index` call.

## Impact Explanation
`OutgoingToken` is a credential associated with a bridge/external-adapter integration. Exposing it to any authenticated user — including low-privileged `View`/`Run` role accounts that are explicitly barred from bridge mutation — breaks the role-based access boundary the rest of the bridge API enforces. This is a legitimate cross-role information disclosure of a secret that a lower-privileged principal should not be able to read, mapping to the "key/secret exfiltration" and "node API authentication/role bypass" impact classes.

## Likelihood Explanation
Exploitation requires only a valid authenticated session or API token of any role (e.g., `View`), which is a normal, low-privilege credential a node operator may legitimately grant to a monitoring/dashboard user. No race condition, admin access, or unusual configuration is required — a single `GET /v2/bridge_types/:BridgeName` (or enumeration via `GET /v2/bridge_types`) suffices and is fully repeatable.

## Recommendation
Apply the same role check used for mutation routes (`auth.RequiresEditRole` or a dedicated read-scope check) to `GET /v2/bridge_types/:BridgeName` and `GET /v2/bridge_types`, or omit/redact `OutgoingToken` from `BridgeResource` for non-privileged roles, mirroring the create-once/`omitempty` handling already used for `IncomingToken`.

## Proof of Concept
1. Create a Chainlink node user with `View` (ReadOnly) role, or issue a View-scoped API token.
2. As that user, confirm `POST /v2/bridge_types` returns 401/Unauthorized (role enforcement works for mutation), per `RequiresEditRole` in `core/web/auth/auth.go`.
3. As the same View-role user, call `GET /v2/bridge_types` to enumerate bridge names, then `GET /v2/bridge_types/<name>` for each.
4. Observe the JSON response includes `"outgoingToken": "<plaintext token>"` for every bridge despite the user lacking Edit/Admin privileges — confirmed by the unconditional field assignment in `presenters.NewBridgeResource` (`core/web/presenters/bridges.go:37`) and the unguarded route registration (`core/web/router.go:271`).

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

**File:** core/web/auth/auth.go (L153-234)
```go
// Authenticate is middleware which authenticates the request by attempting to
// authenticate using all the provided methods.
func Authenticate(store Authenticator, methods ...authMethod) gin.HandlerFunc {
	return func(c *gin.Context) {
		var err error
		for _, method := range methods {
			err = method(c, store)
			if !errors.Is(err, auth.ErrorAuthFailed) {
				break
			}
		}
		if err != nil {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, err)

			return
		}

		c.Next()
	}
}

// GetAuthenticatedUser extracts the authentication user from the context.
func GetAuthenticatedUser(c *gin.Context) (*clsessions.User, bool) {
	obj, ok := c.Get(SessionUserKey)
	if !ok {
		return nil, false
	}

	user, ok := obj.(*clsessions.User)

	return user, ok
}

// GetAuthenticatedExternalInitiator extracts the external initiator from the
// context.
func GetAuthenticatedExternalInitiator(c *gin.Context) (*bridges.ExternalInitiator, bool) {
	obj, ok := c.Get(SessionExternalInitiatorKey)
	if !ok {
		return nil, false
	}

	return obj.(*bridges.ExternalInitiator), ok
}

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
