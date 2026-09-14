### Title
Bridge and External Initiator outgoing tokens (secrets) disclosed to view-only users via unrestricted GET endpoints - ([File: core/web/router.go])

### Summary
`GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, and `GET /v2/external_initiators` are registered under the generic `authv2` group with no role-elevation middleware, so any authenticated user — including the lowest-privileged `view` role (read-only, analogous to Jenkins' `Overall/Read`) — can call them and receive the bridge's `OutgoingToken` and the external initiator's `OutgoingToken`, secrets that should be restricted to higher-privileged roles.

### Finding Description
Chainlink's web API enforces role-based access control via middleware wrappers `auth.RequiresRunRole`, `auth.RequiresEditRole`, `auth.RequiresAdminRole` [1](#0-0) . Routes lacking one of these wrappers are reachable by any authenticated session regardless of role, down to `UserRoleView` [2](#0-1) .

In `v2Routes`, the bridge and external-initiator read endpoints are registered without any such role check: [3](#0-2) 

`BridgeTypesController.Index` and `.Show` both serialize the bridge via `presenters.NewBridgeResource`, which unconditionally includes the `OutgoingToken` field (not `omitempty`, unlike `IncomingToken`): [4](#0-3) [5](#0-4) 

Similarly, `ExternalInitiatorsController.Index` serializes via `presenters.NewExternalInitiatorResource`, which also includes `OutgoingToken`: [6](#0-5) [7](#0-6) 

`OutgoingToken` is a secret used by the node to authenticate itself when calling out to the external adapter/initiator (`bridges.BridgeType.OutgoingToken`, `db:"outgoing_token"`) [8](#0-7) , generated with `utils.NewSecret(24)` [9](#0-8) . This is materially the same bug class as the Jenkins CVE: a low-privilege, read-only authenticated actor can enumerate configured integration metadata that includes sensitive credential material, without the intended stricter permission boundary.

### Impact Explanation
A user granted only the `view` role (intended for read-only dashboard access, no mutation rights) can retrieve `OutgoingToken` values for every configured bridge and external initiator. Since `OutgoingToken` is used to authenticate outbound calls to (or incoming calls from) external adapters/initiators, its disclosure to an unprivileged actor allows impersonation of the node when communicating with those external systems — effectively a credential/secret disclosure and potential request-impersonation vector, exceeding what the `view` role is meant to permit.

### Likelihood Explanation
Any user who already has a `view`-role session or API token (the lowest privilege tier, commonly issued broadly for monitoring/dashboard purposes) can trigger this with a simple authenticated GET request — no additional bypass or race condition needed. The RBAC test suite explicitly documents `bridge_types` and `external_initiators` GET routes as `viewOnlyAllowed: true` [10](#0-9) , confirming this is the deliberately/accidentally allowed current behavior rather than a theoretical gap.

### Recommendation
Restrict `GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, and `GET /v2/external_initiators` to at least `edit` role via `auth.RequiresEditRole`, or strip `OutgoingToken`/other secret fields from the `view`-role response path (e.g., omit unless role check passes in the controller, similar to how `IncomingToken` is only populated at creation time). Apply the same review to any other presenter that unconditionally serializes secret material for `view`-accessible routes.

### Proof of Concept
1. Create/have a user with `UserRoleView` (e.g., via `admin users create --role view`).
2. Authenticate as that user and call `GET /v2/bridge_types` or `GET /v2/external_initiators`.
3. Observe the JSON response includes `outgoingToken` for each configured bridge/initiator, confirming disclosure to a read-only role, as validated by the existing `TestRBAC_Routemap_ViewOnly` test asserting these routes are `viewOnlyAllowed` [11](#0-10) .

### Citations

**File:** core/web/auth/auth.go (L198-253)
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

// RequiresAdminRole extracts the user object from the context, and asserts the user's role is 'admin'
func RequiresAdminRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role != clsessions.UserRoleAdmin {
			c.Abort()
			addForbiddenErrorHeaders(c, "admin", string(user.Role), user.Email)
			jsonAPIError(c, http.StatusForbidden, errors.New("Forbidden"))
			return
		}
		handler(c)
	}
}
```

**File:** core/sessions/user.go (L29-34)
```go
const (
	UserRoleAdmin UserRole = "admin"
	UserRoleEdit  UserRole = "edit"
	UserRoleRun   UserRole = "run"
	UserRoleView  UserRole = "view"
)
```

**File:** core/web/router.go (L263-273)
```go
		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))

		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
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

**File:** core/web/presenters/external_initiators.go (L57-77)
```go
type ExternalInitiatorResource struct {
	JAID
	Name          string         `json:"name"`
	URL           *models.WebURL `json:"url"`
	AccessKey     string         `json:"accessKey"`
	OutgoingToken string         `json:"outgoingToken"`
	CreatedAt     time.Time      `json:"createdAt"`
	UpdatedAt     time.Time      `json:"updatedAt"`
}

func NewExternalInitiatorResource(ei bridges.ExternalInitiator) ExternalInitiatorResource {
	return ExternalInitiatorResource{
		JAID:          NewJAID(strconv.FormatInt(ei.ID, 10)),
		Name:          ei.Name,
		URL:           ei.URL,
		AccessKey:     ei.AccessKey,
		OutgoingToken: ei.OutgoingToken,
		CreatedAt:     ei.CreatedAt,
		UpdatedAt:     ei.UpdatedAt,
	}
}
```

**File:** core/web/external_initiators_controller.go (L50-59)
```go
func (eic *ExternalInitiatorsController) Index(c *gin.Context, size, page, offset int) {
	ctx := c.Request.Context()
	externalInitiators, count, err := eic.App.BridgeORM().ExternalInitiators(ctx, offset, size)
	resources := make([]presenters.ExternalInitiatorResource, 0, len(externalInitiators))
	for _, initiator := range externalInitiators {
		resources = append(resources, presenters.NewExternalInitiatorResource(initiator))
	}

	paginatedResponse(c, "externalInitiators", size, page, resources, count, err)
}
```

**File:** core/bridges/bridge_type.go (L55-68)
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
```

**File:** core/bridges/bridge_type.go (L70-90)
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
```

**File:** core/web/auth/auth_test.go (L224-231)
```go
	{"GET", "/v2/external_initiators", true, true, true},
	{"POST", "/v2/external_initiators", false, false, true},
	{"DELETE", "/v2/external_initiators/MOCK", false, false, true},
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
	{"DELETE", "/v2/bridge_types/MOCK", false, false, true},
```

**File:** core/web/auth/auth_test.go (L484-532)
```go
func TestRBAC_Routemap_ViewOnly(t *testing.T) {
	t.Parallel()
	app := cltest.NewApplicationEVMDisabled(t)
	require.NoError(t, app.Start(t.Context()))

	router := web.Router(t, app, nil)
	ts := httptest.NewServer(router)
	defer ts.Close()

	// Create a test run user to work with
	u := &cltest.User{Role: sessions.UserRoleView}
	client := app.NewHTTPClient(u)

	// Assert all view only routes
	for i, route := range routesRolesMap {
		t.Run(fmt.Sprintf("%d-%s-%s", i, route.verb, route.path), func(t *testing.T) {
			t.Parallel()
			var resp *http.Response
			var cleanup func()

			switch route.verb {
			case "GET":
				resp, cleanup = client.Get(route.path)
			case "POST":
				resp, cleanup = client.Post(route.path, nil)
			case "DELETE":
				resp, cleanup = client.Delete(route.path)
			case "PATCH":
				resp, cleanup = client.Patch(route.path, nil)
			case "PUT":
				resp, cleanup = client.Put(route.path, nil)
			default:
				t.Fatalf("Unknown HTTP verb %s\n", route.verb)
			}
			defer cleanup()

			// If this route only allows view only, don't expect an unauthorized response
			switch {
			case route.viewOnlyAllowed:
				assert.NotEqual(t, http.StatusUnauthorized, resp.StatusCode)
				assert.NotEqual(t, http.StatusForbidden, resp.StatusCode)
			case !route.EditAllowed:
				assert.Equal(t, http.StatusForbidden, resp.StatusCode)
			default:
				assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
			}
		})
	}
}
```
