Audit Report

## Title
Missing role check on `GET /v2/external_initiators` exposes `OutgoingToken` credentials to any authenticated `view`-role user - (File: core/web/router.go)

## Summary
The `authv2` route group registers `GET /v2/external_initiators` (`eia.Index`) with only `paginatedRequest`, while `POST` and `DELETE` on the same resource are wrapped with `auth.RequiresEditRole`. Since the `Index` handler serializes each external initiator via `presenters.ExternalInitiatorResource`, which includes the plaintext `OutgoingToken` field, any user who can authenticate to the node at all — including one explicitly provisioned with the lowest `view` role — can read outgoing webhook secrets belonging to every external initiator on the node, secrets that only `edit`/`admin` users are supposed to manage.

## Finding Description
In `v2Routes`, the routes are: [1](#0-0) 

`authv2` authenticates requests solely via `auth.AuthenticateByToken` and `auth.AuthenticateBySession`: [2](#0-1)  — note `auth.AuthenticateExternalInitiator` is not part of this group (confirmed: no matches for that authenticator in `router.go`), so the "run-role external initiator" escalation path described in the original claim does not apply here. However, the core issue still holds for ordinary node users: `RequiresEditRole` blocks users whose role is `view` or `run` [3](#0-2) , but `Index` has no such wrapper at all, so a `view`-role session/API-token user passes straight through to the handler: [4](#0-3) 

The resource returned embeds the secret: [5](#0-4) , and that secret is generated specifically for the node to authenticate outbound webhook calls to the initiator: [6](#0-5) .

This is a genuine inconsistency: `Create`/`Destroy` are explicitly gated to `edit`+ roles, but `Index`, which discloses the same class of secret material, is left open to any authenticated identity regardless of role.

## Impact Explanation
A node operator can provision multiple users with different roles (`view`, `run`, `edit`, `admin`) via `UserController` (`RequiresAdminRole`-gated `/users` endpoints). A `view`-role user is intended to have read-only, non-sensitive access to the node UI/API, not access to write-level secrets such as outgoing webhook tokens. Because `Index` has no role check, a `view`-role (or `run`-role) authenticated user can retrieve `OutgoingToken` for all external initiators, which could be used to impersonate the node when calling out to the initiator's webhook, or misused against that external system. This maps to an in-scope "key/secret exfiltration" / "node API role bypass" impact category, since the broken assumption is that read access to this collection should be as protected as write access given the secret it exposes.

## Likelihood Explanation
Exploitability requires only that the node has External Initiators enabled and at least one has been created, and that the attacker holds any valid authenticated credential — even the weakest `view` role — which is a legitimately, admin-provisioned lower-privileged account within Chainlink's own multi-role user model (not a "leaked credential" or externally-obtained secret). This satisfies "escalation from an unprivileged starting point" since a `view` user has no rights to create/manage external initiators yet can read their secrets. The claim's alternative vector via `AuthenticateExternalInitiator`/`run`-role auto-assignment does not apply to this route group and should be disregarded, but the `view`-role vector alone is sufficient and directly reproducible.

## Recommendation
Wrap `authv2.GET("/external_initiators", ...)` with `auth.RequiresEditRole` (matching `Create`/`Destroy`), or strip `OutgoingToken`/`OutgoingSecret` from the list/index resource so lower-privileged roles cannot read outgoing webhook credentials.

## Proof of Concept
1. As an admin, enable external initiators (`JobPipeline.ExternalInitiatorsEnabled = true`) and create one via `POST /v2/external_initiators` (persists `OutgoingToken`/`OutgoingSecret`).
2. As an admin, create a second user with role `view` via `POST /v2/users` (`auth.RequiresAdminRole`-gated).
3. Log in as the `view`-role user (session or API token) — this passes `AuthenticateByToken`/`AuthenticateBySession` in `authv2`.
4. Call `GET /v2/external_initiators` with that identity. Since no `RequiresEditRole`/`RequiresRunRole` wrapper exists on this route (`core/web/router.go:264`), the request succeeds (HTTP 200) and the JSON response includes `outgoingToken` for each initiator, confirming disclosure to a role that has no write access to this resource.

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

**File:** core/web/presenters/external_initiators.go (L57-76)
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
```

**File:** core/bridges/external_initiator.go (L38-57)
```go
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
