All claims are confirmed by direct code inspection: the `GET /v2/external_initiators` route lacks any `auth.RequiresEditRole` (or `RequiresRunRole`) wrapper while `Create`/`Destroy` for the same resource require Edit role, and `ExternalInitiatorResource` (returned by `Index`) exposes `AccessKey` and `OutgoingToken` to any authenticated session including View role.Confirmed all elements of the claim. The `authv2` group at `core/web/router.go:245-248` only requires generic session/token authentication (via `auth.Authenticate`), with no role check — `RequiresAdminRole`/`RequiresEditRole`/`RequiresRunRole` are applied selectively per-route, and `/external_initiators` GET (`Index`) at line 264 is missing any such wrapper, unlike `Create`/`Destroy` on lines 265-266 which use `auth.RequiresEditRole`. The `Index` handler and `ExternalInitiatorResource` presenter directly return `AccessKey` and `OutgoingToken` fields.

Audit Report

## Title
Unprivileged (View-role) users can enumerate `OutgoingToken` and `AccessKey` credentials for all External Initiators - (File: core/web/router.go, core/web/external_initiators_controller.go)

## Summary
The `GET /v2/external_initiators` route is registered without any role-requiring wrapper (`authv2.GET("/external_initiators", paginatedRequest(eia.Index))`), while the sibling mutation routes for the same resource require `auth.RequiresEditRole`. As a result, any authenticated user — including one with the lowest `UserRoleView` role — can call this endpoint and receive every registered External Initiator's `AccessKey` and `OutgoingToken` via `ExternalInitiatorResource`.

## Finding Description
In `core/web/router.go`, the `v2Routes` function creates the `authv2` group with only generic session/token authentication middleware (`auth.Authenticate(... AuthenticateByToken, AuthenticateBySession)`), which does not check role at all — role enforcement is applied per-route via explicit wrappers like `auth.RequiresAdminRole`, `auth.RequiresEditRole`, `auth.RequiresRunRole`. The external initiators routes are: `authv2.GET("/external_initiators", paginatedRequest(eia.Index))`, `authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))`, `authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))`. Only `Index` (the read path) lacks any role guard.

`ExternalInitiatorsController.Index` in `core/web/external_initiators_controller.go` fetches all `ExternalInitiator` records and serializes them with `presenters.NewExternalInitiatorResource`, which populates `AccessKey` and `OutgoingToken` fields directly from the stored `bridges.ExternalInitiator` model. `RequiresEditRole` (in `core/web/auth/auth.go`) explicitly blocks `UserRoleView` and `UserRoleRun`, but since `Index` never invokes this check, a `UserRoleView` session/token passes the generic `authv2` authentication and reaches the handler unimpeded. This is confirmed by the existing test `core/web/external_initiators_controller_test.go` which directly asserts `AccessKey`/`OutgoingToken` are present in the `Index` response.

Note that the `IncomingToken`/hashed secret (used to authenticate inbound requests *from* the initiator to Chainlink) is not present in `ExternalInitiatorResource` — only `AccessKey` and `OutgoingToken` (used by Chainlink for *outbound* callbacks) are exposed.

## Impact Explanation
This is an information-disclosure / broken access-control bug: a `View`-role user (or any lower-privilege token holder), who is explicitly prevented from creating or destroying external initiators, can nonetheless read the `AccessKey` and `OutgoingToken` values that only `Edit`/`Admin` roles are meant to manage. This breaks the intended role-boundary invariant enforced consistently elsewhere in the same resource's API (and across most other `authv2` routes in `core/web/router.go`), constituting a node API role-bypass/secret-exfiltration issue in scope for the bounty's "node API authentication or role bypass" / "key/secret exfiltration" categories. It does not by itself grant inbound request forgery capability against Chainlink (since `IncomingToken`/`Secret` is not exposed), so the severity is disclosure of an outbound-authentication secret, not full account takeover.

## Likelihood Explanation
High — exploitation requires only a standard, low-privilege `View` role user/API token, which is a normal and expected access level to grant to dashboards, monitoring, or read-only integrations. The request is a single unauthenticated-by-role `GET /v2/external_initiators` call; no race condition, timing side-channel, or special network position is needed, and the behavior is fully deterministic and repeatable.

## Recommendation
Wrap the `Index` route with the same or a comparably strict role guard used for `Create`/`Destroy`, e.g. `authv2.GET("/external_initiators", auth.RequiresEditRole(paginatedRequest(eia.Index)))`, or alternatively strip `AccessKey`/`OutgoingToken` from `ExternalInitiatorResource` (or redact them for `View`/`Run` roles) so the read endpoint no longer returns privileged secrets to under-privileged callers.

## Proof of Concept
1. As an `admin`/`edit`-role user, create an external initiator: `POST /v2/external_initiators` with body `{"name":"victim-initiator"}`; note the returned `outgoingToken`.
2. Create/obtain a session or API token for a user with role `view` (`UserRoleView`).
3. As the `view` user, call `GET /v2/external_initiators` (optionally with `?page=1`).
4. Observe the JSON response includes `accessKey` and `outgoingToken` fields for `victim-initiator`, identical to values only editable/creatable by `Edit`/`Admin` roles — confirmable directly by extending `core/web/external_initiators_controller_test.go` to authenticate as a `view`-role client instead of the default test client and asserting the response still contains non-empty `AccessKey`/`OutgoingToken`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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
