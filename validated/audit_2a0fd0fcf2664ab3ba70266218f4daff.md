Audit Report

## Title
View-role users can read bridge `outgoingToken` secrets via `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` - (File: core/web/presenters/bridges.go)

## Summary
The `BridgeTypesController.Index` and `.Show` handlers serialize every bridge record through `presenters.NewBridgeResource`, which unconditionally includes the plaintext `OutgoingToken` field (`json:"outgoingToken"`, no redaction/omitempty), while these GET routes are registered without any `RequiresEditRole`/`RequiresAdminRole` wrapper, unlike all mutating bridge routes. As a result, any authenticated user holding only the lowest-privilege `view` role can retrieve the live secret credential the node uses to authenticate itself to external bridge/adapter endpoints.

## Finding Description
`BridgeResource.OutgoingToken` is defined without an `omitempty` tag or any redaction logic, in contrast to `IncomingToken`, which is explicitly `omitempty` and only populated at creation time: [1](#0-0) . `NewBridgeResource` copies `b.OutgoingToken` directly from the DB-backed `bridges.BridgeType` struct into the response with no filtering by caller role: [2](#0-1) .

The route table confirms `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` are registered with no role gate at all (only `POST`/`PATCH`/`DELETE` use `auth.RequiresEditRole`): [3](#0-2) . The controller code performs no additional authorization check before calling the presenter: [4](#0-3) .

This is independently confirmed by the RBAC test matrix, which explicitly asserts `viewOnlyAllowed: true` for both GET bridge-type routes: [5](#0-4) . The role hierarchy defines `view` as a legitimate, distinct, lowest-privilege authenticated role (`UserRoleAdmin`, `UserRoleEdit`, `UserRoleRun`, `UserRoleView`), and `RequiresEditRole`/`RequiresRunRole` middleware exists specifically to exclude `view`-role users from privileged operations elsewhere in the router — but this protection was never applied to the bridge GET endpoints: [6](#0-5) [7](#0-6) .

The `OutgoingToken` is a genuine secret: it is randomly generated via `utils.NewSecret(24)` at bridge creation and stored/served in plaintext, and is the credential the node uses to authenticate itself when calling the configured external adapter URL: [8](#0-7) . The presenter test fixture confirms it is always serialized in the JSON response: [9](#0-8) .

## Impact Explanation
This is a genuine broken access control / secret disclosure: a low-privileged, non-admin, non-edit authenticated user (`view` role, intended for read-only dashboard/monitoring access) can obtain a live outbound authentication credential for any configured bridge without needing edit or admin permissions. This falls into the "key/secret exfiltration" impact category, since the disclosed token is functionally equivalent to a service credential that the node relies on for authenticating to external systems.

## Likelihood Explanation
The exploit requires only a valid `view`-role session — the least privileged non-anonymous role in the RBAC hierarchy — and a single `GET` request to a route with no elevated role check. It is fully reproducible and repeatable, with no race conditions, timing requirements, or special preconditions beyond having any authenticated account, however low-privileged.

## Recommendation
Restrict `outgoingToken` visibility to callers with at least `edit`/`admin` role: either strip/redact the field in `BridgeResource` for `view`-role sessions within `BridgeTypesController.Index`/`Show` (mirroring how `IncomingToken` is only populated on create), or wrap `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` with `auth.RequiresEditRole`.

## Proof of Concept
1. As an admin/edit user, create a bridge via `POST /v2/bridge_types`, noting the `outgoingToken` value returned.
2. Create/authenticate a session for a user with `sessions.UserRoleView`.
3. Issue `GET /v2/bridge_types/<BridgeName>` (or `GET /v2/bridge_types`) using the view-role session cookie/token.
4. Observe the JSON response body includes the plaintext `outgoingToken` field for the bridge, as shown by the fixture in `core/web/presenters/bridges_test.go` and confirmed by the RBAC test asserting `viewOnlyAllowed: true` in `core/web/auth/auth_test.go`.

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

**File:** core/web/auth/auth_test.go (L227-231)
```go
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
	{"DELETE", "/v2/bridge_types/MOCK", false, false, true},
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

**File:** core/bridges/bridge_type.go (L63-76)
```go
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
