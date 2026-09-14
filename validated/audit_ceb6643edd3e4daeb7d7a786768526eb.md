### Title
Missing role-based permission check on GET /v2/external_initiators discloses initiator AccessKey and OutgoingToken to any authenticated 'view' role user - (File: core/web/router.go)

### Summary
The Bitbucket Server plugin CVE (CVE-2022-28134) describes HTTP endpoints that omit permission checks, letting a low-privileged Overall/Read user create, view, and delete Bitbucket Server consumers (which include stored credentials). The chainlink codebase has a directly analogous, unprivileged-reachable bug in its own node HTTP API: the `GET /v2/external_initiators` endpoint is wired without any role gate, while the sibling `POST`/`DELETE` routes for the same resource explicitly require `RequiresEditRole`.

### Finding Description
Chainlink's web API enforces RBAC via `auth.RequiresAdminRole`, `auth.RequiresEditRole`, and `auth.RequiresRunRole` middleware wrappers defined in [1](#0-0) . Route registration in `v2Routes` deliberately applies these wrappers per-endpoint, e.g. for external initiators: [2](#0-1) 

Note that `Create` and `Destroy` are wrapped with `auth.RequiresEditRole`, but `Index` (the `GET` list handler) is registered with only `paginatedRequest(eia.Index)` — no role check at all, meaning any authenticated user, including one with the lowest `UserRoleView` role, can call it.

`ExternalInitiatorsController.Index` returns the full list of external initiators via `presenters.NewExternalInitiatorResource`: [3](#0-2) 

That presenter serializes each initiator's `AccessKey` and `OutgoingToken` in the JSON API response: [4](#0-3) 

These are the credentials used for `AuthenticateExternalInitiator`, i.e., they can be replayed to trigger job runs as that external initiator: [5](#0-4) 

The test suite's own RBAC route map confirms the endpoint is intentionally treated as accessible to `view` role, corroborating the missing/absent explicit role check: [6](#0-5) 

### Impact Explanation
Any user provisioned with the lowest privilege role (`view`, intended for read-only dashboards) — or any external-initiator/API-token holder authenticated at that level — can enumerate all configured external initiators and obtain their `AccessKey` and `OutgoingToken` secret material. `OutgoingToken`, combined with the corresponding secret already known to the initiator, can be used to impersonate the external initiator and trigger job runs (`POST /v2/jobs/:ID/runs`) or forge outgoing webhook payloads, since `AuthenticateExternalInitiator` implicitly grants the caller `UserRoleRun`. This is a secret-disclosure and request-impersonation vector reachable by a low-privileged authenticated user, matching the CWE-862 (missing authorization) pattern from the reference CVE.

### Likelihood Explanation
Likelihood is moderate: it requires the attacker to hold any valid Chainlink node API session/token, even with the most restricted `view` role — a role explicitly designed to have no mutation privileges. Given that `view` accounts may be issued more broadly (e.g., to monitoring/read-only tooling or less-trusted operators), and the endpoint requires no special exploit beyond a normal GET request, exploitation is straightforward once such credentials exist.

### Recommendation
Wrap the `GET /v2/external_initiators` route with an appropriate role-check middleware (at minimum `auth.RequiresEditRole`, matching `Create`/`Destroy`, or `RequiresAdminRole` given the sensitivity of the returned secrets) in `core/web/router.go`, e.g.:
```go
authv2.GET("/external_initiators", auth.RequiresEditRole(paginatedRequest(eia.Index)))
```
Additionally, consider redacting `AccessKey`/`OutgoingToken` from list responses entirely (only surfacing new secrets once, at creation time, as is already done via `ExternalInitiatorAuthentication`), consistent with typical secret-handling practice elsewhere in the codebase.

### Proof of Concept
1. Provision or obtain a Chainlink node account/API token with `UserRoleView` (lowest privilege).
2. Authenticate to the node's web API (session cookie or API token) as that view-only user.
3. Issue `GET /v2/external_initiators` — this succeeds and returns JSON API resources containing `accessKey` and `outgoingToken` for every registered external initiator (per `core/web/external_initiators_controller.go` `Index` and `presenters.ExternalInitiatorResource`), despite the same user being forbidden from `POST`/`DELETE` on the identical resource path.
4. Use the leaked `outgoingToken` (with the initiator's known/leaked secret) to authenticate as that external initiator and call `POST /v2/jobs/:ID/runs`, triggering job runs the view-only user was never authorized to invoke.

### Citations

**File:** core/web/auth/auth.go (L119-148)
```go
func AuthenticateExternalInitiator(c *gin.Context, store Authenticator) error {
	ctx := c.Request.Context()
	eia := &auth.Token{
		AccessKey: c.GetHeader(static.ExternalInitiatorAccessKeyHeader),
		Secret:    c.GetHeader(static.ExternalInitiatorSecretHeader),
	}

	ei, err := store.FindExternalInitiator(ctx, eia)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return auth.ErrorAuthFailed
		}

		return errors.Wrap(err, "finding external initiator")
	}

	ok, err := bridges.AuthenticateExternalInitiator(eia, ei)
	if err != nil {
		return err
	}
	if !ok {
		return auth.ErrorAuthFailed
	}

	// External initiator endpoints (wrapped with AuthenticateExternalInitiator) inherently assume the role
	// of 'run' (required to trigger job runs)
	c.Set(SessionExternalInitiatorKey, ei)
	c.Set(SessionUserKey, &clsessions.User{Role: clsessions.UserRoleRun})

	return nil
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

**File:** core/web/router.go (L263-266)
```go
		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
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

**File:** core/web/auth/auth_test.go (L224-224)
```go
	{"GET", "/v2/external_initiators", true, true, true},
```
