Based on the investigation, the `ExternalInitiatorsController.Index` endpoint is a valid analog to the CVE-2021-20250 pattern (a route reachable by an under-privileged authenticated caller that returns data it should not).

### Title
Unprivileged view-role users can enumerate External Initiator access keys and outgoing secrets via `GET /v2/external_initiators` - (File: core/web/router.go)

### Summary
The JBoss EJB Client CVE describes privileged actions being reachable by callers who should not have that access, leading to information disclosure. In chainlink-024, the `/v2/external_initiators` route is registered without any role gate, so any authenticated user — including one with the lowest `UserRoleView` role — can list all configured External Initiators, exposing each initiator's `AccessKey` and `OutgoingToken`/`OutgoingSecret` fields.

### Finding Description
In `core/web/router.go`, the route is wired as: [1](#0-0) 
`authv2.GET("/external_initiators", paginatedRequest(eia.Index))` has no `auth.RequiresEditRole`/`RequiresAdminRole` wrapper, unlike the `Create`/`Destroy` routes on the same block which are wrapped with `auth.RequiresEditRole`.

`ExternalInitiatorsController.Index` returns `presenters.ExternalInitiatorResource` for every stored initiator: [2](#0-1) 

The presenter includes the initiator's `AccessKey` and `OutgoingToken`: [3](#0-2) 

`OutgoingToken`/`OutgoingSecret` are randomly generated secrets used by the node to authenticate to the external initiator when triggering webhooks: [4](#0-3) 

The route only requires an authenticated session/token (`authv2` group uses `auth.AuthenticateByToken`/`auth.AuthenticateBySession`), with no additional role check: [5](#0-4) 

### Impact Explanation
A user with the lowest privilege role (`view`) can read the `AccessKey` and `OutgoingToken` for every External Initiator configured in the node. `OutgoingToken`/`OutgoingSecret` are meant to authenticate the node to the external system, and `AccessKey` is part of the credential external systems use to call back into the node (paired with a secret at creation time, though the raw `Secret`/`HashedSecret` is not returned by `Index`). Exposure of these values to unprivileged users breaks the intended role segmentation (view < run < edit < admin) and could facilitate request impersonation against systems trusting these initiators.

### Likelihood Explanation
Any authenticated user, regardless of role, can trigger this by issuing `GET /v2/external_initiators`; no special conditions or races are required. All that's needed is a valid session/API token with `view` role, which is the least privileged tier in the RBAC model.

### Recommendation
Wrap the `Index` route with a role guard consistent with the other mutating routes in the same controller block, e.g. `auth.RequiresEditRole(paginatedRequest(eia.Index))`, or filter the presenter to omit `OutgoingToken` for callers below the `edit`/`admin` role.

### Proof of Concept
1. Create a user with `UserRoleView` (e.g., via `RequiresAdminRole`-gated `/v2/users` as an admin, or use an existing view-role session).
2. As an admin, create an External Initiator: `POST /v2/external_initiators` with `{"name":"test-ei"}` (requires edit role) — the response includes `outgoingToken`.
3. Log in as the view-role user and call `GET /v2/external_initiators`.
4. Observe the response contains the same `accessKey` and `outgoingToken` for `test-ei`, despite the caller only holding `view` role — confirmed by the missing role wrapper at [6](#0-5)  compared to the `RequiresEditRole` wrapper used on `Create`/`Destroy`.

Note: I could not fully verify runtime behavior (e.g., whether any middleware elsewhere implicitly restricts `Index`); this assessment is based on static route wiring in `core/web/router.go`. A background Devin session with full repo/test execution access would be needed to confirm behavior end-to-end and check for related overrides I may not have found via search.

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

**File:** core/bridges/external_initiator.go (L21-57)
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

// NewExternalInitiator generates an ExternalInitiator from an
// auth.Token, hashing the password for storage
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
