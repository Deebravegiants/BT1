All claims in the report are verified against the actual source code. The `GET /v2/external_initiators` route at [1](#0-0)  indeed lacks any `auth.RequiresXRole` wrapper, unlike the `Create` (`RequiresEditRole`) and `Destroy` (`RequiresEditRole`) routes on the same lines. The `authv2` group only requires generic authentication via `auth.Authenticate` with `AuthenticateByToken`/`AuthenticateBySession` [2](#0-1) , which succeeds for any valid user regardless of role — confirmed by `RequiresEditRole` and `RequiresRunRole` explicitly checking `user.Role` after authentication succeeds [3](#0-2) , proving that plain `Authenticate` alone does not gate by role.

The `Index` handler fetches and serializes all External Initiators including `OutgoingToken` via `presenters.NewExternalInitiatorResource` [4](#0-3) [5](#0-4) , confirming the secret leakage.

Audit Report

## Title
Missing role check on `GET /v2/external_initiators` leaks all External Initiators' `OutgoingToken` secrets to any authenticated low-privilege user - (File: core/web/router.go)

## Summary
The `/v2/external_initiators` `GET` (`Index`) route is registered without any role restriction, while the `POST` (`Create`) and `DELETE` (`Destroy`) routes for the same resource require `auth.RequiresEditRole`. Any user authenticated with even the lowest privilege level (`view`) can call this endpoint and receive the `OutgoingToken` secret for every External Initiator configured on the node.

## Finding Description
In `core/web/router.go`, the External Initiator routes are registered as `authv2.GET("/external_initiators", paginatedRequest(eia.Index))`, `authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))`, and `authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))`. Only `GET` lacks a role wrapper. It inherits only the generic `authv2` group authentication (`AuthenticateByToken` or `AuthenticateBySession`), which authenticates any valid user token/session regardless of role — role enforcement is a separate, explicit step performed only by wrappers like `RequiresEditRole`/`RequiresRunRole`/`RequiresAdminRole`. Since `Index` has no such wrapper, the handler executes for any authenticated user of any role (including `view`). The handler retrieves all External Initiators via `BridgeORM().ExternalInitiators` and serializes each with `presenters.NewExternalInitiatorResource`, which includes the `OutgoingToken` field — a secret generated at creation time that the node uses to authenticate outbound webhook calls to the external initiator.

## Impact Explanation
A user provisioned with only the `view` role (a legitimate, commonly-issued minimal-privilege credential for dashboards/monitoring) can read `OutgoingToken` secrets belonging to every External Initiator on the node, not just ones they should have access to. This is a concrete secret/key exfiltration vulnerability enabling impersonation of the node's outgoing webhook calls to the initiator's own service, matching an in-scope "key/secret exfiltration" and "node API authentication/role bypass" impact category.

## Likelihood Explanation
Exploitation requires only a valid `view`-role (or any-role) session/token and a single `GET` request — no special conditions, admin access, or complex setup. Any deployment that issues `view`-role users for read-only dashboard purposes is immediately exposed.

## Recommendation
Wrap `Index` with `auth.RequiresEditRole` (or at minimum `RequiresRunRole`) in `core/web/router.go`, matching protection on `Create`/`Destroy`. Additionally, consider excluding `OutgoingToken`/`OutgoingSecret` from list responses entirely, returning them only once at creation via `NewExternalInitiatorAuthentication`.

## Proof of Concept
1. Provision a `view`-role user or API token (via admin-only user management endpoints).
2. Authenticate as that user (`POST /sessions` for session cookie, or `X-API-KEY`/`X-API-SECRET` headers for token auth) — both succeed regardless of role per `AuthenticateBySession`/`AuthenticateByToken`.
3. Send `GET /v2/external_initiators` with the `view` credentials.
4. Observe the JSON:API response includes `outgoingToken` for every configured External Initiator, which a `view`-role user should never be entitled to read.

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
