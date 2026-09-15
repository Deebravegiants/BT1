Audit Report

## Title
Missing role check on `GET /v2/external_initiators` exposes `OutgoingToken` credentials to any authenticated view-role user - (File: core/web/router.go)

## Summary
In `v2Routes`, the external initiator routes apply `auth.RequiresEditRole` to `Create` and `Destroy`, but `Index` is registered with no role check at all — only the outer `authv2` group's session/token authentication applies. [1](#0-0)  Since `Index` returns `presenters.ExternalInitiatorResource`, which includes the `OutgoingToken` secret, any user who can authenticate to the node with any role — including the lowest-privilege `view` role, which by design should never see write-oriented resources or secrets — can read every external initiator's outgoing webhook credential.

## Finding Description
The `authv2` route group requires only `AuthenticateByToken` or `AuthenticateBySession`, with no role gating applied by default. [2](#0-1)  Individual routes then apply role-specific wrappers such as `auth.RequiresEditRole` or `auth.RequiresAdminRole`. For external initiators, `Create` and `Destroy` are wrapped in `auth.RequiresEditRole`, but `Index` is wrapped only in `paginatedRequest`, with no role check: [1](#0-0) 

The `Index` handler in `ExternalInitiatorsController` fetches all external initiators and serializes them via `presenters.NewExternalInitiatorResource`, with no field redaction: [3](#0-2) 

That presenter includes the `OutgoingToken` field, which is a secret generated specifically so the node can authenticate itself against the initiator's webhook: [4](#0-3) [5](#0-4) 

`auth.RequiresEditRole` blocks users with `UserRoleView` or `UserRoleRun`, reserving write endpoints for `edit`/`admin` roles: [6](#0-5)  Because `Index` has none of this gating, a `view`-role user — who by design should only have read access to non-sensitive resources and no ability to create/manage external initiators — can nonetheless read secrets that only edit/admin users are supposed to control or generate. This is inconsistent with how the sibling routes (`Create`/`Destroy`) are protected and represents a genuine confidentiality gap, since `Index` is the only place `OutgoingToken` is exposed in bulk to any authenticated identity regardless of role.

Note: the claim's PoC reference to `AuthenticateExternalInitiator` auto-granting `UserRoleRun` access into this route is not accurate — that auth method is not included in `authv2`'s `Authenticate(... AuthenticateByToken, AuthenticateBySession)` chain, so external-initiator identities cannot reach this route via that mechanism. However, the core vulnerability — any authenticated node user, including one restricted to the `view` role, can list all external initiators and obtain their `OutgoingToken` — is confirmed directly from the code and doesn't depend on that faulty vector.

## Impact Explanation
Exposure of `OutgoingToken` lets a low-privileged authenticated node user (one who should be restricted to read-only, non-sensitive data) obtain credentials the node uses to authenticate itself when calling out to external initiator webhooks. This falls into the key/secret exfiltration impact category: a `view`-role account, which an admin may issue for dashboards or monitoring with no intent to grant credential access, can silently harvest webhook secrets for every external initiator configured on the node.

## Likelihood Explanation
Likelihood is moderate to high in environments where External Initiators are enabled and multiple user roles exist. The exploit requires only a valid session or API token of any role (including `view`) — no edit/admin privilege, database access, or host access is needed, and the request is a single unauthenticated-role-check `GET /v2/external_initiators` call.

## Recommendation
Wrap `authv2.GET("/external_initiators", ...)` with a role guard (at minimum `auth.RequiresEditRole` matching `Create`/`Destroy`, or a dedicated `RequiresRunRole`/`RequiresAdminRole` if broader read access is intended), or strip `OutgoingToken`/`OutgoingSecret` from the resource returned by `Index` so that view-only or non-privileged authenticated users cannot read outgoing webhook credentials.

## Proof of Concept
1. Enable external initiators (`JobPipeline.ExternalInitiatorsEnabled = true`).
2. As an admin, create an external initiator via `POST /v2/external_initiators`; the resulting record's `OutgoingToken`/`OutgoingSecret` are persisted (`core/bridges/external_initiator.go`, `NewExternalInitiator`).
3. Create or use a session/API token belonging to a `view`-role user (`clsessions.UserRoleView`).
4. Call `GET /v2/external_initiators` using that `view`-role identity's session cookie or `X-API-KEY`/`X-API-SECRET` headers. Because `core/web/router.go:264` applies no role wrapper, the request succeeds (only `AuthenticateByToken`/`AuthenticateBySession` from the `authv2` group is enforced) and the JSON response body includes each initiator's `outgoingToken` field, per `core/web/presenters/external_initiators.go:57-76`.
5. Compare with the same `view`-role user attempting `POST`/`DELETE` on the same endpoint, which correctly returns `401 Unauthorized` due to `auth.RequiresEditRole`, confirming the inconsistency is specific to `Index`.

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
