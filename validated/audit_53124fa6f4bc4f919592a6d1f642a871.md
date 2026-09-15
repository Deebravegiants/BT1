All claims are verified directly against the code. The `Index` route registration at `core/web/router.go` L264 lacks any role-check wrapper (`paginatedRequest(eia.Index)`), while `Create` and `Destroy` on the same resource at L265-266 are explicitly wrapped in `auth.RequiresEditRole`. The `authv2` group only enforces authentication (valid session/token), not role, as shown in `core/web/auth/auth.go` L155-173 vs the role-checking functions `RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole` at L200-253. The `Index` handler in `core/web/external_initiators_controller.go` L50-59 performs no additional role check and serializes `presenters.ExternalInitiatorResource`, which embeds `AccessKey` and `OutgoingToken` in plaintext JSON (`core/web/presenters/external_initiators.go` L57-77). This is confirmed by the existing test `TestExternalInitiatorsController_Index` in `core/web/external_initiators_controller_test.go` L108-109, L125-126, which asserts these secret fields are returned to any authenticated client with no role restriction applied.

Audit Report

## Title
View-role users can read External Initiator `AccessKey`/`OutgoingToken` secrets via unauthenticated-role-gated `GET /v2/external_initiators` - (File: core/web/router.go)

## Summary
The `/v2/external_initiators` listing endpoint is registered in `v2Routes` without any role guard (`authv2.GET("/external_initiators", paginatedRequest(eia.Index))`), while the sibling `Create` and `Destroy` routes on the same resource explicitly require `auth.RequiresEditRole`. Any authenticated user — including one with the lowest `UserRoleView` role — can therefore call this endpoint and receive every stored external initiator's plaintext `AccessKey` and `OutgoingToken`.

## Finding Description
In `core/web/router.go`, the external-initiator routes are:
```go
authv2.GET("/external_initiators", paginatedRequest(eia.Index))
authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
```
The `authv2` group (`core/web/router.go` L245-248) only wraps requests in `auth.Authenticate` with `AuthenticateByToken`/`AuthenticateBySession`, which validates that a request comes from *some* authenticated user, but performs no role check (`core/web/auth/auth.go` L155-173). The codebase's actual role-enforcement primitives (`RequiresRunRole`, `RequiresEditRole`, `RequiresAdminRole`, `core/web/auth/auth.go` L198-253) explicitly check `user.Role`, but `Index` is not wrapped in any of them. The `Index` handler itself (`core/web/external_initiators_controller.go` L50-59) performs no supplemental authorization check and unconditionally returns `presenters.ExternalInitiatorResource` for every row, which includes `AccessKey` and `OutgoingToken` fields (`core/web/presenters/external_initiators.go` L57-77). This is directly confirmed by the existing test `TestExternalInitiatorsController_Index`, which asserts the plaintext `AccessKey`/`OutgoingToken` values are present in the response for a client with no elevated role configured.

## Impact Explanation
`AccessKey` and `OutgoingToken` are authentication-adjacent credentials for the external initiator subsystem: `AccessKey` is used (paired with the separately-stored, not-returned `Secret`/`HashedSecret`) to authenticate inbound external-initiator job-trigger requests, and `OutgoingToken` is used by the node to authenticate itself when calling out to the initiator's webhook. Exposing these to `view`-role users breaks the least-privilege model that this exact controller otherwise enforces (`Create`/`Destroy` require `edit`), constituting an authorization/role-check inconsistency and secret-exposure issue. This maps to the in-scope "key/secret exfiltration" impact category, though full compromise additionally requires the corresponding `Secret`, which is not exposed by this endpoint.

## Likelihood Explanation
Trivially and repeatably triggerable: any authenticated user, including a `UserRoleView` session/API-token holder, can call `GET /v2/external_initiators` (or its paginated variant) with no special preconditions and immediately receive the secret fields for all initiators.

## Recommendation
Wrap the `GET /v2/external_initiators` route with `auth.RequiresEditRole` (matching `Create`/`Destroy`), or remove `AccessKey`/`OutgoingToken` from `ExternalInitiatorResource` used by `Index`/`Show`-style listing endpoints, restricting secret visibility to the one-time `Create` response (`ExternalInitiatorAuthentication`) only.

## Proof of Concept
1. Create a user with `sessions.UserRoleView` (e.g., via `RequiresAdminRole`-gated `POST /v2/users`, performed once by an admin, or in a test harness via `cltest`).
2. Authenticate as that view-role user and call `GET /v2/external_initiators`.
3. Observe the JSON response includes `accessKey` and `outgoingToken` for every configured external initiator — reproduced by the existing unit test `TestExternalInitiatorsController_Index` in `core/web/external_initiators_controller_test.go` (L108-109, L125-126), which does not assert or require an elevated role for the requesting client, and by comparison, attempting the same client against `POST /v2/external_initiators` or `DELETE /v2/external_initiators/:Name` would be rejected by `auth.RequiresEditRole` for a view-role user. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** core/web/router.go (L245-266)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
	{
		uc := UserController{app}
		authv2.GET("/users", auth.RequiresAdminRole(uc.Index))
		authv2.POST("/users", auth.RequiresAdminRole(uc.Create))
		authv2.PATCH("/users", auth.RequiresAdminRole(uc.UpdateRole))
		authv2.DELETE("/users/:email", auth.RequiresAdminRole(uc.Delete))
		authv2.PATCH("/user/password", uc.UpdatePassword)
		authv2.POST("/user/token", uc.NewAPIToken)
		authv2.POST("/user/token/delete", uc.DeleteAPIToken)

		wa := NewWebAuthnController(app)
		authv2.GET("/enroll_webauthn", wa.BeginRegistration)
		authv2.POST("/enroll_webauthn", wa.FinishRegistration)

		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
```

**File:** core/web/auth/auth.go (L155-234)
```go
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

**File:** core/web/external_initiators_controller_test.go (L104-126)
```go
	assert.Len(t, externalInitiators, 1)
	assert.Equal(t, strconv.FormatInt(eiBar.ID, 10), externalInitiators[0].ID)
	assert.Equal(t, eiBar.Name, externalInitiators[0].Name)
	assert.Nil(t, externalInitiators[0].URL)
	assert.Equal(t, eiBar.AccessKey, externalInitiators[0].AccessKey)
	assert.Equal(t, eiBar.OutgoingToken, externalInitiators[0].OutgoingToken)

	resp, cleanup = client.Get(links["next"].Href)
	t.Cleanup(cleanup)
	cltest.AssertServerResponse(t, resp, http.StatusOK)

	externalInitiators = []presenters.ExternalInitiatorResource{}
	err = web.ParsePaginatedResponse(cltest.ParseResponseBody(t, resp), &externalInitiators, &links)
	require.NoError(t, err)
	assert.Empty(t, links["next"])
	assert.NotEmpty(t, links["prev"])

	assert.Len(t, externalInitiators, 1)
	assert.Equal(t, strconv.FormatInt(eiFoo.ID, 10), externalInitiators[0].ID)
	assert.Equal(t, eiFoo.Name, externalInitiators[0].Name)
	assert.Equal(t, eiFoo.URL.String(), externalInitiators[0].URL.String())
	assert.Equal(t, eiFoo.AccessKey, externalInitiators[0].AccessKey)
	assert.Equal(t, eiFoo.OutgoingToken, externalInitiators[0].OutgoingToken)
```
