### Title
Missing role check on External Initiator listing endpoint discloses AccessKey/OutgoingToken to any authenticated user - (File: core/web/router.go)

### Summary
The Jenkins Publish Over FTP CVE stems from a missing permission check that let low-privileged users leverage stored, attacker-reachable credentials for an outbound connection. The chainlink node has an analogous gap: while creating/deleting External Initiator (EI) credentials correctly enforces `auth.RequiresEditRole`, the endpoint that lists them does not enforce any role check at all.

### Finding Description
In `core/web/router.go`, the External Initiator routes are registered as: [1](#0-0) 

`POST` and `DELETE` are wrapped in `auth.RequiresEditRole`, but `GET /v2/external_initiators` (`eia.Index`) is only guarded by the generic `authv2` group middleware, which just requires *any* valid session or API token (`auth.AuthenticateByToken`/`auth.AuthenticateBySession`) — no role check: [2](#0-1) 

The `Index` handler returns every configured External Initiator, serialized with `presenters.NewExternalInitiatorResource`, which includes `AccessKey` and `OutgoingToken`: [3](#0-2) [4](#0-3) 

`AccessKey` is the identifier used together with the (not returned) `Secret` to authenticate as an External Initiator via `AuthenticateExternalInitiator`, and `OutgoingToken`/`OutgoingSecret` are the credentials generated for the node to use when calling back out to the initiator's configured URL: [5](#0-4) [6](#0-5) 

So any authenticated user — even one holding only the lowest role — can enumerate `AccessKey` and `OutgoingToken` values for all External Initiators, credentials that the mutation endpoints (`Create`/`Destroy`) are explicitly gated behind `RequiresEditRole` to protect.

### Impact Explanation
This is a credential/secret-disclosure issue analogous to the CVE's "attacker with lesser permission gains access to credential material intended for privileged use." Exposure of `AccessKey`/`OutgoingToken` to any authenticated (low-role) user undermines the role-separation the rest of the External Initiator API enforces, and could facilitate impersonation or reconnaissance against the External Initiator/outgoing-webhook flow.

### Likelihood Explanation
Any user who can authenticate to the node at all (session or API token, regardless of assigned role) can hit `GET /v2/external_initiators` — no special conditions or elevated access needed, since the route only requires successful `authv2` authentication with no role gate.

### Recommendation
Add a role check (e.g., `auth.RequiresEditRole` or `auth.RequiresRunRole`, consistent with the sensitivity of `AccessKey`/`OutgoingToken`) to the `GET /v2/external_initiators` route, matching the protection already applied to `Create`/`Destroy`. Consider also excluding `OutgoingToken`/`AccessKey` from list responses entirely, similar to how `Secret`/`OutgoingSecret` are already omitted from `ExternalInitiatorResource`.

### Proof of Concept
1. Authenticate as any node user (or use any valid API token) with the lowest available role.
2. Issue `GET /v2/external_initiators`.
3. Observe the response includes `accessKey` and `outgoingToken` for every configured External Initiator, per `presenters.ExternalInitiatorResource` in `core/web/presenters/external_initiators.go`, despite `POST`/`DELETE` on the same resource requiring `RequiresEditRole` in `core/web/router.go`.

Note: I was unable to locate the exact call site that consumes `OutgoingToken`/`OutgoingSecret` when the node calls out to an External Initiator's URL, so the precise mechanics of how this token is used for outbound authentication are inferred from field naming/comments in `core/bridges/external_initiator.go` rather than directly confirmed in code I retrieved.

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

**File:** core/bridges/external_initiator.go (L36-67)
```go
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

// AuthenticateExternalInitiator compares an auth against an initiator and
// returns true if the password hashes match
func AuthenticateExternalInitiator(eia *auth.Token, ea *ExternalInitiator) (bool, error) {
	hashedSecret, err := auth.HashedSecret(eia, ea.Salt)
	if err != nil {
		return false, err
	}
	return subtle.ConstantTimeCompare([]byte(hashedSecret), []byte(ea.HashedSecret)) == 1, nil
}
```

**File:** core/web/auth/auth.go (L116-149)
```go
// AuthenticateExternalInitiator authenticates an external initiator request.
//
// Implements authMethod
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
