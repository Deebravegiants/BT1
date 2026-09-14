### Title
Missing role-based permission check on `GET /v2/external_initiators` allows low-privileged users to enumerate External Initiator access keys - ([File: core/web/router.go])

### Summary
The route `GET /v2/external_initiators`, handled by `ExternalInitiatorsController.Index`, is registered without any `auth.RequiresEditRole`/`auth.RequiresAdminRole` wrapper, unlike its sibling `POST`/`DELETE` routes on the same resource. Any authenticated node user — including the lowest-privileged `UserRoleView` role — can call this endpoint to enumerate all configured External Initiators, including their plaintext `AccessKey` and `OutgoingToken` fields.

### Finding Description
In `v2Routes`, the External Initiators routes are defined as: [1](#0-0) 

Only the `POST` (create) and `DELETE` (destroy) actions require `auth.RequiresEditRole`. The `GET` (`Index`) action has no role check at all — it only passes through the generic `authv2` group's authentication middleware (`auth.AuthenticateByToken`/`auth.AuthenticateBySession`), which merely verifies the caller is *some* logged-in user, without checking role: [2](#0-1) 

`ExternalInitiatorsController.Index` then returns all external initiators, including their `AccessKey` (identifier) and `OutgoingToken` fields, sourced directly from the ORM without redaction: [3](#0-2) [4](#0-3) 

This is directly analogous to the Jenkins GCE plugin bug class: an endpoint that should require an elevated permission (here, `edit`/`admin` role, consistent with the other mutating endpoints on the same resource) instead only checks for basic authentication, permitting a low-privileged, authenticated-but-unprivileged actor (`UserRoleView`) to enumerate credential identifiers belonging to the system.

Compare this to the pattern used correctly elsewhere in the same file for VRF keys, jobs, bridge types, etc., where `GET` list/read handlers are left open only when they don't expose secrets, and sensitive/mutating actions are gated with `RequiresEditRole`/`RequiresAdminRole`: [5](#0-4) 

The RBAC role model itself is defined in `core/web/auth/auth.go`, where `UserRoleView` is explicitly the lowest role and is excluded from `RequiresEditRole`/`RequiresAdminRole`-protected actions: [6](#0-5) 

### Impact Explanation
`AccessKey` is one of the two credential components (`AccessKey`/`Secret`) used to authenticate as an External Initiator against the node's `/v2/*` "external initiator" endpoints via `AuthenticateExternalInitiator`: [7](#0-6) 

While the hashed `Secret` itself is not returned by `Index` (only `AccessKey`/`OutgoingToken` are exposed per `ExternalInitiatorResource`), disclosure of valid `AccessKey` identifiers and `OutgoingToken` values to an unprivileged view-only user still constitutes unauthorized information disclosure of node-level integration credentials that a "view" role should not be entitled to see, weakening the access-control boundary between roles and facilitating further attacks (e.g., targeted secret-guessing/brute force against a known valid `AccessKey`, or misuse of `OutgoingToken` if it's used to validate outbound webhook calls from the node to the initiator).

### Likelihood Explanation
Likelihood is high for any deployment that has multiple API users with different roles (a supported, documented feature — `UserRoleView`, `UserRoleRun`, `UserRoleEdit`, `UserRoleAdmin`). Any user granted only `view` access (e.g., a read-only dashboard/monitoring account) can call this endpoint with valid session/API-token credentials and receive full initiator listings, requiring no additional privilege escalation.

### Recommendation
Wrap the `GET /v2/external_initiators` route with `auth.RequiresEditRole` (matching the `POST`/`DELETE` handlers on the same resource) or `auth.RequiresAdminRole`, e.g.:
```go
authv2.GET("/external_initiators", auth.RequiresEditRole(paginatedRequest(eia.Index)))
```
Additionally consider whether `AccessKey`/`OutgoingToken` should be redacted from list responses entirely, similar to how `Secret`/`OutgoingSecret` are excluded from `ExternalInitiatorResource`.

### Proof of Concept
1. Create an API user with `UserRoleView` (lowest role) via the admin `POST /v2/users` endpoint.
2. Log in as that view-only user (`POST /sessions`) or use their API token.
3. Call `GET /v2/external_initiators` with the view-only session/token — request succeeds (no `RequiresEditRole`/`RequiresAdminRole` check exists on this route), returning JSON with all initiators' `accessKey` and `outgoingToken` fields, as validated by the existing test asserting these fields are populated in the `Index` response: [8](#0-7)

### Citations

**File:** core/web/router.go (L245-248)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
```

**File:** core/web/router.go (L263-266)
```go
		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
```

**File:** core/web/router.go (L378-396)
```go
		vrfkc := VRFKeysController{app}
		authv2.GET("/keys/vrf", vrfkc.Index)
		authv2.POST("/keys/vrf", auth.RequiresEditRole(vrfkc.Create))
		authv2.DELETE("/keys/vrf/:keyID", auth.RequiresAdminRole(vrfkc.Delete))
		authv2.POST("/keys/vrf/import", auth.RequiresAdminRole(vrfkc.Import))
		authv2.POST("/keys/vrf/export/:keyID", auth.RequiresAdminRole(vrfkc.Export))

		wfkc := WorkflowKeysController{app}
		authv2.GET("/keys/workflow", wfkc.Index)

		dkrkc := DKGRecipientKeysController{app}
		authv2.GET("/keys/dkgrecipient", dkrkc.Index)

		jc := JobsController{app}
		authv2.GET("/jobs", paginatedRequest(jc.Index))
		authv2.GET("/jobs/:ID", jc.Show)
		authv2.POST("/jobs", auth.RequiresEditRole(jc.Create))
		authv2.PUT("/jobs/:ID", auth.RequiresEditRole(jc.Update))
		authv2.DELETE("/jobs/:ID", auth.RequiresEditRole(jc.Delete))
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

**File:** core/web/auth/auth.go (L119-149)
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
}
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

**File:** core/web/external_initiators_controller_test.go (L104-109)
```go
	assert.Len(t, externalInitiators, 1)
	assert.Equal(t, strconv.FormatInt(eiBar.ID, 10), externalInitiators[0].ID)
	assert.Equal(t, eiBar.Name, externalInitiators[0].Name)
	assert.Nil(t, externalInitiators[0].URL)
	assert.Equal(t, eiBar.AccessKey, externalInitiators[0].AccessKey)
	assert.Equal(t, eiBar.OutgoingToken, externalInitiators[0].OutgoingToken)
```
