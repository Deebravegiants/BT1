This confirms all the claims in the report. Let me verify the external initiators controller and check for any known-issue exclusions.All the claims in the report are verified accurately against the current codebase.

Audit Report

## Title
Unprivileged "view"-role users can read External Initiator and Bridge secrets via unguarded Index endpoints - ([File: core/web/router.go])

## Summary
`GET /v2/external_initiators` and `GET /v2/bridge_types` are registered in `v2Routes` with only `paginatedRequest(...Index)`, unlike their `Create`/`Update`/`Destroy` siblings which are wrapped in `auth.RequiresEditRole`. Since the enclosing `authv2` group only enforces generic authentication (`auth.Authenticate`) and not role checks, any authenticated user — including one with the lowest-privileged `UserRoleView` — can call these endpoints and receive `AccessKey`/`OutgoingToken` secret material for every configured External Initiator and Bridge.

## Finding Description
In `core/web/router.go`, the `authv2` group is created with only session/token authentication middleware: [1](#0-0) 

The External Initiator and Bridge Type routes are registered such that `Index` has no role wrapper, while `Create`, `Update`, and `Destroy` are explicitly wrapped in `auth.RequiresEditRole`: [2](#0-1) 

`auth.Authenticate` verifies only that a valid session/token exists, performing no role check: [3](#0-2) 

Role enforcement exists only in `RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole`, and must be applied per-route — it is not applied to `Index` for these two controllers: [4](#0-3) 

`ExternalInitiatorsController.Index` returns all stored initiators serialized through `presenters.ExternalInitiatorResource`, which includes `AccessKey` and `OutgoingToken`: [5](#0-4) [6](#0-5) 

Similarly, `BridgeTypesController.Index` returns all bridges via `presenters.BridgeResource`, which includes `OutgoingToken` unconditionally (only `IncomingToken` is gated by `omitempty` and only populated at creation time): [7](#0-6) [8](#0-7) 

These are genuine credentials: `AccessKey`/`HashedSecret` authenticate inbound External-Initiator-triggered job runs, and `OutgoingSecret`/`OutgoingToken` are used by the node to authenticate itself back to the External Initiator service: [9](#0-8) 

No other guard (redaction, response filtering, additional middleware) exists on these `Index` routes to compensate for the missing role check.

## Impact Explanation
This maps to the in-scope "key/secret exfiltration" and "node API role bypass" impact categories. A user provisioned only with `UserRoleView` — intended to be strictly read-only for dashboards/monitoring and unable to create/modify jobs, bridges, or initiators — can retrieve `AccessKey` and `OutgoingToken` for every External Initiator and Bridge on the node via a plain authenticated `GET`. Disclosure of `OutgoingToken` allows impersonating the node when calling back to the EI service, and `AccessKey` (combined with further leakage of the hashed secret's plaintext form via other channels, or job triggering knowledge) undermines the intended EI authentication boundary. This is a real violation of the role-separation model that the rest of the `/v2` API otherwise enforces consistently (e.g. `/users`, transfers, `Create`/`Update`/`Destroy` on these same resources).

## Likelihood Explanation
High. Any operator who provisions a `view`-role account — a common low-trust delegation pattern — automatically grants secret-reading capability with a single GET request, no timing or race conditions required, fully reproducible via normal API calls with only view-level credentials.

## Recommendation
Wrap `authv2.GET("/external_initiators", ...)` and `authv2.GET("/bridge_types", ...)` (and `bt.Show`) with at least `auth.RequiresEditRole`, matching the mutating verbs, or strip `AccessKey`/`OutgoingToken` from resources returned to non-edit/admin roles. Audit all `authv2` routes for the same "missing role wrapper on GET/list, present on mutating verbs" pattern (e.g. `/bridge_types/:BridgeName` `Show` also has no role wrapper and returns `OutgoingToken`).

## Proof of Concept
1. As admin, create a `UserRoleView` user (`POST /v2/users` with `role=view`) and an External Initiator (`POST /v2/external_initiators`) and/or Bridge (`POST /v2/bridge_types`).
2. Authenticate as the view-role user (session cookie or API token).
3. `GET /v2/external_initiators` — response JSON includes `accessKey` and `outgoingToken` fields per [10](#0-9) .
4. `GET /v2/bridge_types` — response JSON includes `outgoingToken` per [11](#0-10) .
5. Confirm via `core/web/auth/auth.go`'s `RequiresEditRole` that the same view-role user is correctly rejected (401) on `POST /v2/external_initiators` or `POST /v2/bridge_types`, demonstrating the inconsistency between mutating and list endpoints.

### Citations

**File:** core/web/router.go (L245-248)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
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

**File:** core/web/auth/auth.go (L153-173)
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
```

**File:** core/web/auth/auth.go (L198-230)
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

**File:** core/bridges/external_initiator.go (L21-34)
```go
// ExternalInitiator represents a user that can initiate runs remotely
type ExternalInitiator struct {
	ID             int64
	Name           string
	URL            *models.WebURL
	AccessKey      string
	Salt           string
	HashedSecret   string
	OutgoingSecret string
	OutgoingToken  string

	CreatedAt time.Time
	UpdatedAt time.Time
}
```
