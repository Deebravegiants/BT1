### Title
Unprivileged `view`-role users can list Bridge and External Initiator secrets (`OutgoingToken`/`AccessKey`) via unauthenticated-role-gated endpoints - (File: core/web/router.go)

### Summary
`GET /v2/bridge_types` and `GET /v2/external_initiators` are registered with no role-restricting middleware (only session/token authentication), so any authenticated user — including the lowest-privilege `view` role — can list all bridges and external initiators, including their `OutgoingToken` and `AccessKey` secret fields. This mirrors the CVE-2019-11294 bug class: an unprivileged/low-privilege actor can enumerate resources and their sensitive URLs/tokens that should be restricted to higher-privileged roles.

### Finding Description
The v2 router wires these two index routes only through the generic `paginatedRequest` wrapper, without any `auth.RequiresEditRole` / `auth.RequiresAdminRole` gate, unlike almost every other mutating or sensitive route in the same file: [1](#0-0) 

Compare this to the `POST`/`PATCH`/`DELETE` routes for the same resources, which do require `auth.RequiresEditRole`, confirming that write access is intentionally role-gated while read access to the Index endpoints is left open to any authenticated role.

The `RequiresEditRole` middleware in `core/web/auth/auth.go` explicitly blocks `view` and `run` roles from “edit” actions, showing the app’s security model treats `view` as a strictly read-limited role for sensitive resources: [2](#0-1) 

However, the `Index` handlers for both resources serialize secrets directly into the response body:
- `ExternalInitiatorsController.Index` returns `presenters.ExternalInitiatorResource`, which includes `AccessKey` and `OutgoingToken`: [3](#0-2) [4](#0-3) 
- `BridgeTypesController.Index` returns `presenters.BridgeResource`, which includes `OutgoingToken`: [5](#0-4) [6](#0-5) 

The project's own RBAC regression test (`core/web/auth/auth_test.go`) codifies this behavior as `viewOnlyAllowed: true` for both `GET /v2/external_initiators` and `GET /v2/bridge_types`: [7](#0-6) 

This is the same bug class as CVE-2019-11294: a low-privilege actor (Cloud Foundry "space developer" ↔ chainlink `view` role) is able to list resources — including their URLs/tokens — that should be gated to a more privileged role (Cloud Foundry "admin" ↔ chainlink `edit`/`admin`), because the listing endpoint lacks the write-endpoints' authorization check.

### Impact Explanation
`OutgoingToken` (bridge/external-initiator outgoing token) and `AccessKey` are credentials used to authenticate calls to/from external adapters and external initiators. Any authenticated node user with only `view` privileges (e.g., a read-only operator-UI account explicitly created for monitoring/auditing per the CHANGELOG's RBAC feature) can retrieve these secrets and impersonate the bridge/initiator relationship, or use the leaked URL/token to interact with the external adapter/initiator endpoint outside of the node. This is a credential-disclosure/cross-privilege issue, not a full compromise, hence the moderate severity consistent with the CVE's CVSS.

### Likelihood Explanation
Likelihood is high for any deployment that issues `view`-role API users (the RBAC feature's stated purpose — “readonly user … can log in to the Operator UI independently”). No additional exploitation steps beyond an authenticated GET request are required; the vulnerable route is directly reachable and returns full secret fields in the response body as shown in the existing test `TestExternalInitiatorsController_Index`, which asserts `AccessKey` and `OutgoingToken` are present in the list response: [8](#0-7) 

### Recommendation
Gate `GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, `GET /v2/external_initiators` with at least `auth.RequiresEditRole` (matching the write endpoints for the same resources), or strip `OutgoingToken`/`AccessKey` from the `Index`/`Show` presenter output for lower-privilege roles, exposing secrets only on creation as already done for `IncomingToken`/`Secret`.

### Proof of Concept
1. Create a `view`-role API user: `chainlink admin users create --email=viewer@test.com --role=view`.
2. Authenticate as that user and issue `GET /v2/external_initiators` (or `GET /v2/bridge_types`).
3. Observe the JSON response includes `accessKey` and `outgoingToken` (or `outgoingToken` for bridges) for every configured resource, even though the same user receives `403 Forbidden` when attempting `POST`/`PATCH`/`DELETE` on the identical resource.

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

**File:** core/web/bridge_types_controller.go (L111-122)
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

**File:** core/web/external_initiators_controller_test.go (L104-109)
```go
	assert.Len(t, externalInitiators, 1)
	assert.Equal(t, strconv.FormatInt(eiBar.ID, 10), externalInitiators[0].ID)
	assert.Equal(t, eiBar.Name, externalInitiators[0].Name)
	assert.Nil(t, externalInitiators[0].URL)
	assert.Equal(t, eiBar.AccessKey, externalInitiators[0].AccessKey)
	assert.Equal(t, eiBar.OutgoingToken, externalInitiators[0].OutgoingToken)
```
