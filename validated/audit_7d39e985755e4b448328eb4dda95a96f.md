### Title
View-role authenticated users can read all External Initiators' `AccessKey`/`OutgoingToken` request-impersonation credentials via `GET /v2/external_initiators` - (File: core/web/external_initiators_controller.go)

### Summary
`GET /v2/external_initiators` is reachable by any authenticated node user, including the lowest privilege `view` role, and returns the `AccessKey` and `OutgoingToken` for every External Initiator configured on the node — not just initiators the requesting user created or manages.

### Finding Description
The route is registered without any role-gating middleware, unlike almost every other sensitive resource in the router: [1](#0-0) 

Compare this to sibling endpoints in the same route group that do enforce `auth.RequiresEditRole`/`auth.RequiresAdminRole` for create/update/delete, but leave `Index` (list) completely unrestricted beyond basic authentication.

The handler queries and returns every stored External Initiator record for the whole node: [2](#0-1) 

The presenter used for the list explicitly serializes the `AccessKey` and `OutgoingToken` fields: [3](#0-2) 

The `OutgoingToken` is a per-initiator secret generated at creation time (`utils.NewSecret(utils.DefaultSecretSize)`) that the node uses to authenticate itself when calling out to that External Initiator's webhook: [4](#0-3) 

The `AccessKey`, together with the caller-supplied `Secret`, is exactly what the node's `AuthenticateExternalInitiator` function checks to authenticate *inbound* requests from an External Initiator that trigger job runs (assuming `run` role): [5](#0-4) 

The project's own RBAC regression test explicitly documents and asserts that this route is reachable by `view`-role users (`viewOnlyAllowed: true`), confirming the exposure is not accidental in test coverage, but the underlying design still permits any authenticated user — regardless of role — to enumerate all initiators' identifying/secret material: [6](#0-5) [7](#0-6) 

This mirrors the CVE-2020-12687 bug class: an endpoint intended for administrative/bridge-management use returns cross-tenant/cross-resource secret material (attachments in Serpico; `AccessKey`/`OutgoingToken` here) to a non-privileged authenticated caller who has no legitimate need to see other initiators' credentials.

### Impact Explanation
An attacker who obtains even the lowest-privilege (`view`) API credential for the node can enumerate every External Initiator's `AccessKey` and `OutgoingToken`. With the `AccessKey` known, the attacker only needs to also learn/brute-force the initiator's `Secret` (not returned here) to forge inbound authenticated requests that trigger job runs as that initiator. Regardless, disclosure of `OutgoingToken`/`AccessKey` values across all initiators to unprivileged users breaks the intended per-initiator secret boundary and constitutes credential disclosure beyond the caller's authorization scope, analogous to Serpico's admin-only attachment data being retrievable by non-admin users.

### Likelihood Explanation
Likelihood is limited by the fact that `view` role API access itself must be provisioned by an admin, and the External Initiator feature must be enabled (`ExternalInitiatorsEnabled`). However, once any authenticated API user account exists (even `view`), no additional privilege escalation or exploit is required — a single unauthenticated-role-gated GET request discloses the data, matching the "low complexity, low privilege required" profile of the CVE.

### Recommendation
Restrict `GET /v2/external_initiators` with `auth.RequiresEditRole` or `auth.RequiresAdminRole` (consistent with the `Create`/`Destroy` handlers on the same resource), or strip `AccessKey`/`OutgoingToken` from the list presenter and only expose them at creation time (as is already done for `Secret`/`OutgoingSecret`, which use `omitempty` and are only populated in the one-time `Create` response).

### Proof of Concept
1. Provision or obtain an API user with `view` role.
2. Authenticate a session/token and call:
   ```
   GET /v2/external_initiators?size=100
   ```
3. Observe the JSON:API response includes `accessKey` and `outgoingToken` attributes for every External Initiator configured on the node, confirmed by the existing test assertions: [8](#0-7)

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

**File:** core/bridges/external_initiator.go (L36-57)
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
```

**File:** core/web/auth/auth.go (L116-148)
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
```

**File:** core/web/auth/auth_test.go (L224-224)
```go
	{"GET", "/v2/external_initiators", true, true, true},
```

**File:** core/web/auth/auth_test.go (L484-532)
```go
func TestRBAC_Routemap_ViewOnly(t *testing.T) {
	t.Parallel()
	app := cltest.NewApplicationEVMDisabled(t)
	require.NoError(t, app.Start(t.Context()))

	router := web.Router(t, app, nil)
	ts := httptest.NewServer(router)
	defer ts.Close()

	// Create a test run user to work with
	u := &cltest.User{Role: sessions.UserRoleView}
	client := app.NewHTTPClient(u)

	// Assert all view only routes
	for i, route := range routesRolesMap {
		t.Run(fmt.Sprintf("%d-%s-%s", i, route.verb, route.path), func(t *testing.T) {
			t.Parallel()
			var resp *http.Response
			var cleanup func()

			switch route.verb {
			case "GET":
				resp, cleanup = client.Get(route.path)
			case "POST":
				resp, cleanup = client.Post(route.path, nil)
			case "DELETE":
				resp, cleanup = client.Delete(route.path)
			case "PATCH":
				resp, cleanup = client.Patch(route.path, nil)
			case "PUT":
				resp, cleanup = client.Put(route.path, nil)
			default:
				t.Fatalf("Unknown HTTP verb %s\n", route.verb)
			}
			defer cleanup()

			// If this route only allows view only, don't expect an unauthorized response
			switch {
			case route.viewOnlyAllowed:
				assert.NotEqual(t, http.StatusUnauthorized, resp.StatusCode)
				assert.NotEqual(t, http.StatusForbidden, resp.StatusCode)
			case !route.EditAllowed:
				assert.Equal(t, http.StatusForbidden, resp.StatusCode)
			default:
				assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
			}
		})
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
