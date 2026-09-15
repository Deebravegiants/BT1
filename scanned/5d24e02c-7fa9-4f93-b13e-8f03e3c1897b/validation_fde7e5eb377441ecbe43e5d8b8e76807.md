### Title
Unprivileged "view"-role users can read External Initiator and Bridge secrets via unguarded Index endpoints - ([File: core/web/router.go])

### Summary
The `GET /v2/external_initiators` and `GET /v2/bridge_types` endpoints are mounted without any per-role guard, while their sibling `Create`/`Update`/`Destroy` actions are explicitly wrapped with `auth.RequiresEditRole`. As a result, any authenticated node user — including the lowest-privileged `UserRoleView` — can list all configured External Initiators and Bridges and read their `AccessKey` and `OutgoingToken` fields, which are credential material intended to be restricted to edit/admin-level operators.

### Finding Description
`v2Routes` registers the External Initiator and Bridge Type collections like this: [1](#0-0) 

Note that `Index` (the `GET` list endpoint) has no role wrapper at all, while `Create`, `Update`, and `Destroy` are wrapped in `auth.RequiresEditRole`. The only gate applied to the whole `/v2` group is generic authentication: [2](#0-1) 

`auth.Authenticate` only verifies that *some* valid session or API token exists — it does not check role: [3](#0-2) 

Role enforcement is implemented separately via `RequiresRunRole` / `RequiresEditRole` / `RequiresAdminRole`, which must be explicitly applied per-route: [4](#0-3) 

Because `Index` for `ExternalInitiatorsController` and `BridgeTypesController` omit these wrappers, any authenticated user — even one created with `UserRoleView` (read-only) — can call `Index` and receive the full credential set.

`ExternalInitiatorsController.Index` returns every stored `ExternalInitiator`, serialized through a resource type that includes the `AccessKey` and `OutgoingToken`: [5](#0-4) [6](#0-5) 

These are genuine secrets: `AccessKey`/secret pairs authenticate External Initiator-triggered job runs against the node (`AuthenticateExternalInitiator`, header-based), and `OutgoingToken`/`OutgoingSecret` are the credentials the node uses to authenticate itself when calling back out to the External Initiator service: [7](#0-6) 

The equivalent `BridgeTypesController.Index`/bridge resource exposes `OutgoingToken` the same way, again without any role restriction on the `GET /v2/bridge_types` route.

This is structurally analogous to the Audius root cause in the sense that a privilege boundary intended to gate a specific class of sensitive operation (there: governance/admin control via storage collision; here: role-based access control on secret-bearing resources) is not actually enforced on all code paths that reach the same underlying state — allowing a caller with lower privilege than intended to obtain material that should only be available to edit/admin-level actors.

### Impact Explanation
A user provisioned only with `UserRoleView` (meant to be read-only and unable to create/modify bridges, initiators, jobs, or transfers) can nonetheless retrieve `AccessKey`/`OutgoingToken` values for every External Initiator and Bridge configured on the node. `OutgoingToken`/`OutgoingSecret` are used by the node to authenticate itself against the External Initiator's HTTP endpoint — disclosure of this token allows a low-privileged internal actor (or anyone able to obtain view-level credentials) to impersonate the node when calling the EI service, or to combine the exposed `AccessKey` with further reconnaissance to attempt to trigger job runs. This breaks the intended role separation between `view`, `run`, `edit`, and `admin` roles that the rest of the API enforces consistently.

### Likelihood Explanation
Any operator who provisions a `view`-role account (a common, low-trust delegation pattern for dashboards/monitoring) automatically gains this secret-reading capability with a single unauthenticated-role-check GET request — no additional exploitation steps, timing, or race conditions are required. Likelihood is high wherever multiple user roles are provisioned on a node.

### Recommendation
Wrap the `Index` handlers for `ExternalInitiatorsController` and `BridgeTypesController` with at least `auth.RequiresEditRole` (matching `Create`/`Update`/`Destroy`), or strip `AccessKey`/`OutgoingToken` from the resources returned to non-edit/admin roles. Audit all other `authv2` routes for the same "missing role wrapper on GET/list, present on mutating verbs" pattern.

### Proof of Concept
1. As an admin, create a user with `UserRoleView` (`POST /v2/users` with `role=view`) and an External Initiator (`POST /v2/external_initiators`).
2. Authenticate the API as the `view`-role user (session cookie or API token).
3. Issue `GET /v2/external_initiators` — the JSON response includes `accessKey` and `outgoingToken` for the initiator created in step 1, despite the requesting user having only view privileges: [8](#0-7) [9](#0-8) 
4. Repeat with `GET /v2/bridge_types` to confirm the same disclosure of `outgoingToken` for Bridges.

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
