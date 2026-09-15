### Title
View-role users can read External Initiator `AccessKey` and `OutgoingToken` via unauthenticated-role `GET /v2/external_initiators` - (File: core/web/external_initiators_controller.go)

### Summary
The `GET /v2/external_initiators` endpoint is wired without any role-elevation middleware, so any authenticated node UI/API user — including the lowest-privilege `view` role — can enumerate all configured External Initiators and receive their `AccessKey` and `OutgoingToken` values in the response.

### Finding Description
The router mounts `Index` for external initiators behind only the generic session/token authenticator, not `RequiresEditRole`/`RequiresRunRole`, unlike `Create`/`Destroy` on the same resource: [1](#0-0) 

The handler returns every stored initiator's `AccessKey` and `OutgoingToken` in the JSON:API response: [2](#0-1) [3](#0-2) 

`AccessKey` is one half of the credential pair used by `AuthenticateExternalInitiator` middleware (paired with a `Secret` that is only returned once, at creation time, and never persisted in plaintext): [4](#0-3) [5](#0-4) 

`OutgoingToken` is the credential the node uses/exposes for the initiator's outgoing webhook callback authentication, so its disclosure to a low-privilege internal user is itself a secret-leak, and its pairing with `AccessKey` (which is one factor needed to attempt initiator authentication, though not sufficient alone since `Secret` is hashed and salted) increases the attack surface for any actor who already holds session/API-token access but was only granted `view` privileges.

This class of bug matches the "unprivileged actor gains an entitlement it should not have" bug class from the referenced incident: a component/role that was meant to be restricted (here, `view`-only users) can pull credential material intended for higher-privilege administration of External Initiators, mirroring how a low-trust integration (MEE6) was able to reach into scopes/roles it wasn't meant to control.

The project's own RBAC test suite documents this as intentional behavior — `viewOnlyAllowed: true` for this route — confirming the route was deliberately left unrestricted rather than gated to `edit`/`admin`, unlike the sibling `Create`/`Destroy` routes on the same resource: [6](#0-5) 

### Impact Explanation
A `view`-role user (the lowest privilege API/UI role in Chainlink node's RBAC model: `admin > edit > run > view`) can read `AccessKey` and `OutgoingToken` for all configured External Initiators, information that is otherwise gated to `edit`/`admin` for mutation. While the `Secret` needed to fully authenticate as an External Initiator is not returned by `Index` (only by `Create`), this still constitutes disclosure of authentication material and metadata to a role that has no operational need for it, violating the principle of least privilege and potentially aiding further attack chaining (e.g., social engineering, correlating `OutgoingToken` with external systems, or facilitating brute-force/timing attacks against the `Secret` half if leaked elsewhere).

### Likelihood Explanation
Any node operator that provisions `view`-role users (e.g., for dashboards/monitoring) is affected, since no additional privilege is required beyond basic node API authentication (session cookie or API token) — this is a directly reachable, unauthenticated-role-bypass path within the existing RBAC model, not requiring any misconfiguration beyond default routing.

### Recommendation
Wrap `GET /v2/external_initiators` with `auth.RequiresEditRole` (matching `Create`/`Destroy` on the same resource), and/or omit `AccessKey`/`OutgoingToken` from the `Index` response for roles below `edit`, only returning non-sensitive fields (`Name`, `URL`, `CreatedAt`, `UpdatedAt`) to `view`/`run` roles.

### Proof of Concept
1. Provision a Chainlink node user with role `view` (`sessions.UserRoleView`).
2. Authenticate as that user (session cookie or API token).
3. Issue `GET /v2/external_initiators` (as exercised by `TestExternalInitiatorsController_Index`): [7](#0-6) 
4. Observe the response contains `accessKey` and `outgoingToken` fields for every configured External Initiator, despite the requesting user holding only `view` privileges.

### Citations

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

**File:** core/web/auth/auth_test.go (L224-224)
```go
	{"GET", "/v2/external_initiators", true, true, true},
```

**File:** core/web/external_initiators_controller_test.go (L84-109)
```go
	resp, cleanup := client.Get("/v2/external_initiators?size=x")
	t.Cleanup(cleanup)
	cltest.AssertServerResponse(t, resp, http.StatusUnprocessableEntity)

	resp, cleanup = client.Get("/v2/external_initiators?size=1")
	t.Cleanup(cleanup)
	cltest.AssertServerResponse(t, resp, http.StatusOK)
	body := cltest.ParseResponseBody(t, resp)

	metaCount, err := cltest.ParseJSONAPIResponseMetaCount(body)
	require.NoError(t, err)
	require.Equal(t, 2, metaCount)

	var links jsonapi.Links
	var externalInitiators []presenters.ExternalInitiatorResource
	err = web.ParsePaginatedResponse(body, &externalInitiators, &links)
	require.NoError(t, err)
	assert.NotEmpty(t, links["next"].Href)
	assert.Empty(t, links["prev"].Href)

	assert.Len(t, externalInitiators, 1)
	assert.Equal(t, strconv.FormatInt(eiBar.ID, 10), externalInitiators[0].ID)
	assert.Equal(t, eiBar.Name, externalInitiators[0].Name)
	assert.Nil(t, externalInitiators[0].URL)
	assert.Equal(t, eiBar.AccessKey, externalInitiators[0].AccessKey)
	assert.Equal(t, eiBar.OutgoingToken, externalInitiators[0].OutgoingToken)
```
