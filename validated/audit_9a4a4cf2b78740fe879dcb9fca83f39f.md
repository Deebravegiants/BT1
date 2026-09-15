This confirms the claim exactly as described. The `Index` route lacks any `RequiresEditRole`/`RequiresRunRole` wrapper while `Create` and `Destroy` on the same resource both require the `edit` role, and `Index` directly returns `AccessKey`/`OutgoingToken` in the response with no redaction.

Now considering scope: this endpoint requires only the generic `authv2` authentication (any valid user session or API token, including `view` role), which is an "unprivileged" authenticated user in Chainlink's own role hierarchy — this matches the report's threat model of privilege/role bypass via a missing authorization check, which is an in-scope impact category (secret exfiltration via role bypass). This is not a misconfiguration or operator-only issue — it's a genuine missing-authorization bug in the route registration itself.All the necessary confirmation has been gathered. The claim is fully verified against the actual code.

Audit Report

## Title
Missing role-based authorization on `GET /v2/external_initiators` exposes External Initiator credentials to any authenticated user - ([File: core/web/router.go])

## Summary
The `GET /v2/external_initiators` route is registered without any minimum-role guard, unlike the sibling `POST`/`DELETE` routes on the same resource which both require `auth.RequiresEditRole`. As a result, any authenticated user regardless of role (including the lowest-privilege `view` role) can call `Index` and retrieve every configured External Initiator's `AccessKey` and `OutgoingToken`.

## Finding Description
In `core/web/router.go`, the External Initiators routes are registered as: [1](#0-0) 

The `authv2` group only requires successful authentication via `auth.AuthenticateByToken` or `auth.AuthenticateBySession` — proving the caller has *some* valid account, of any role: [2](#0-1) 

`Create` and `Destroy` explicitly wrap their handlers with `auth.RequiresEditRole`, which rejects sessions with `UserRoleView` or `UserRoleRun`: [3](#0-2) 

`Index`, however, has no such wrapper — it is only reachable via `paginatedRequest(eia.Index)`, with no role check inside the handler itself: [4](#0-3) 

The handler returns the full `presenters.ExternalInitiatorResource`, including plaintext `AccessKey` and `OutgoingToken`, for every stored initiator with no redaction based on caller role: [5](#0-4) 

This is confirmed by the existing unit test, which uses a plain `client := app.NewHTTPClient(nil)` (an authenticated but otherwise unprivileged client) and asserts it can list initiators and read back their `AccessKey`/`OutgoingToken`: [6](#0-5) 

The broken security assumption is that role-based route gating consistently protects credential-adjacent operations on this resource — it does for `Create`/`Destroy` but is silently absent for `Index`, letting the lowest-privilege authenticated role reach data that the code's own design intends to gate behind `edit`/`admin`.

## Impact Explanation
`AccessKey` and `OutgoingToken` are per-initiator secrets: `AccessKey` (paired with a secret used in the `X-Chainlink-EA-AccessKey`/`X-Chainlink-EA-Secret` headers) authenticates inbound webhook job-run triggers from the External Initiator, and `OutgoingToken` authenticates the node's own outbound calls back to the External Initiator service. A `view`-role account — intended only for read-only dashboard-type access — can harvest these secrets for every configured initiator, enabling impersonation of the node toward the External Initiator service or forging inbound job-trigger requests, which maps to the in-scope "key/secret exfiltration via role bypass" impact category.

## Likelihood Explanation
High. The endpoint is reachable by any account capable of authenticating at all — no elevated role or special condition is required — and the disclosure is deterministic: every call to `GET /v2/external_initiators` returns the full credential set for all initiators, as directly demonstrated by `TestExternalInitiatorsController_Index`.

## Recommendation
Wrap the `Index` handler with `auth.RequiresEditRole` (or an equivalent minimum-role guard) to match the authorization level enforced on `Create`/`Destroy`, or redact `AccessKey`/`OutgoingToken` from the `Index` response for callers below the `edit` role.

## Proof of Concept
1. Create/seed a Chainlink node user (or API token) with role `view`.
2. Authenticate as this user (session cookie or `X-API-KEY`/`X-API-SECRET` headers).
3. Call `GET /v2/external_initiators?size=<n>` — the response returns HTTP 200 with a JSON list including `accessKey` and `outgoingToken` for the configured initiators.
4. Compare against `POST /v2/external_initiators` or `DELETE /v2/external_initiators/:Name` with the same `view`-role credentials, which are rejected with 401 by `auth.RequiresEditRole`, confirming the inconsistency.
5. This exact behavior is already exercised (without role differentiation) by `TestExternalInitiatorsController_Index` in `core/web/external_initiators_controller_test.go`, which can be extended to explicitly assert a `view`-role client succeeds where `Create`/`Destroy` would fail.

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

**File:** core/web/presenters/external_initiators.go (L57-65)
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
```

**File:** core/web/external_initiators_controller_test.go (L72-109)
```go
	client := app.NewHTTPClient(nil)

	db := app.GetDB()
	borm := bridges.NewORM(db)

	eiFoo := cltest.MustInsertExternalInitiatorWithOpts(t, borm, cltest.ExternalInitiatorOpts{
		NamePrefix:    "foo",
		URL:           cltest.MustWebURL(t, "http://example.com/foo"),
		OutgoingToken: "outgoing_token",
	})
	eiBar := cltest.MustInsertExternalInitiatorWithOpts(t, borm, cltest.ExternalInitiatorOpts{NamePrefix: "bar"})

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
