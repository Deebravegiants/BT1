I have enough evidence to answer. The "external report" here is essentially a prompt asking me to find an analogous IDOR/secret-disclosure bug in this Chainlink codebase. Chainlink is a single-tenant node (no per-user data ownership like Chat2DB's multi-tenant datasources), so a literal IDOR analog doesn't exist. However, there is a real, concretely-supported analog: unauthenticated-role-scoping gap that discloses outgoing webhook credentials to any authenticated session regardless of role.

### Title
Unauthenticated-role disclosure of ExternalInitiator OutgoingToken/OutgoingSecret via GET /v2/external_initiators - (File: core/web/external_initiators_controller.go)

### Summary
The `GET /v2/external_initiators` (and `GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`) endpoints are reachable by any authenticated session regardless of role — including the lowest-privilege `UserRoleView` role — and return the `OutgoingToken`/`OutgoingSecret` fields, which are secrets the node uses to authenticate itself to external initiators/bridge adapters.

### Finding Description
The route table registers these endpoints without any role-gating middleware, unlike sibling mutating routes on the same resources which are wrapped in `auth.RequiresEditRole`: [1](#0-0) 

`ExternalInitiatorsController.Index` loads all external initiators and serializes them via `presenters.NewExternalInitiatorResource`, which includes the `OutgoingToken` field: [2](#0-1) [3](#0-2) 

Similarly, `BridgeTypesController.Show`/`Index` return `OutgoingToken` via `presenters.NewBridgeResource`: [4](#0-3) [5](#0-4) 

These tokens are generated as high-entropy secrets when the resource is created (`utils.NewSecret(utils.DefaultSecretSize)`), and are explicitly meant to authenticate outbound requests from the node to the external system, not to be broadly readable: [6](#0-5) 

The project's own RBAC test suite documents and asserts that these GET routes are `viewOnlyAllowed: true`, i.e., intentionally accessible to the lowest role: [7](#0-6) 

### Impact Explanation
Any authenticated Chainlink Operator UI user — even one provisioned with the minimal `UserRoleView` role (intended for read-only dashboard access, no job/bridge management) — can retrieve `OutgoingToken`/`OutgoingSecret` for every configured bridge and external initiator on the node. This is a secret-disclosure/role-bypass issue: a viewer-role principal obtains credentials that let them impersonate the node when calling out to external adapters/initiators, exceeding their intended privilege boundary (view roles are barred from `RequiresRunRole`/`RequiresEditRole` actions elsewhere, e.g. [8](#0-7) , but not from this secret read).

### Likelihood Explanation
Any operator that provisions "view"-role accounts for auditors/dashboards/read-only tooling (a common, encouraged practice) inadvertently grants those accounts access to live outgoing bridge/EI credentials with a single unauthenticated-role `GET` call — no additional exploitation steps required.

### Recommendation
Gate `GET /v2/external_initiators`, `GET /v2/bridge_types`, and `GET /v2/bridge_types/:BridgeName` behind at least `auth.RequiresEditRole` (matching the mutating routes), or strip `OutgoingToken`/`OutgoingSecret` from the presenters used by these read endpoints for non-privileged roles.

### Proof of Concept
1. Create a node user with `UserRoleView` via `POST /v2/users` (admin-only, one-time setup).
2. Log in as that view-role user, obtain a session cookie via `POST /sessions`.
3. Call `GET /v2/external_initiators` — response includes `outgoingToken` for every configured external initiator, per `presenters.ExternalInitiatorResource.OutgoingToken` field [9](#0-8) .
4. Call `GET /v2/bridge_types` — response includes `outgoingToken` for every bridge, per `presenters.BridgeResource.OutgoingToken` field [10](#0-9) .

### Citations

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

**File:** core/bridges/external_initiator.go (L36-57)
```go
// NewExternalInitiator generates an ExternalInitiator from an
// auth.Token, hashing the password for storage
func NewExternalInitiator(
	eia *auth.Token,
	eir *ExternalInitiatorRequest,
) (*ExternalInitiator, error) {
	salt := utils.NewSecret(utils.DefaultSecretSize)
	hashedSecret, err := auth.HashedSecret(eia, salt)
	if err != nil {
		return nil, pkgerrors.Wrap(err, "error hashing secret for external initiator")
	}

	return &ExternalInitiator{
		Name:           strings.ToLower(eir.Name),
		URL:            eir.URL,
		AccessKey:      eia.AccessKey,
		HashedSecret:   hashedSecret,
		Salt:           salt,
		OutgoingToken:  utils.NewSecret(utils.DefaultSecretSize),
		OutgoingSecret: utils.NewSecret(utils.DefaultSecretSize),
	}, nil
}
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
