Audit Report

## Title
Missing role-based access control on `GET /v2/external_initiators` allows low-privilege (`view`/`run`) authenticated users to exfiltrate plaintext `AccessKey`/`OutgoingToken` secrets - ([File: core/web/router.go], [File: core/web/external_initiators_controller.go], [File: core/web/presenters/external_initiators.go])

## Summary
The External Initiator `Index` (list) route is registered without any role-gating middleware, unlike its sibling `Create`/`Destroy` routes which require `auth.RequiresEditRole`. As a result, any authenticated node user — including the lowest-privilege `view` role and the `run` role — can call `GET /v2/external_initiators` and receive the plaintext `AccessKey` and `OutgoingToken` for every configured external initiator, secrets that are otherwise gated behind edit/admin privileges everywhere else in the EI lifecycle.

## Finding Description
In `core/web/router.go`, the EI routes are registered as:
```go
authv2.GET("/external_initiators", paginatedRequest(eia.Index))
authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
``` [1](#0-0) 

`Create` and `Destroy` correctly require `UserRoleEdit` or above via `RequiresEditRole`, which rejects `view` and `run` roles: [2](#0-1)  But `Index` only sits behind the generic `authv2` group, which merely requires a valid session/token (`AuthenticateByToken`/`AuthenticateBySession`) with no role check at all: [3](#0-2) 

`Index` then returns `AccessKey` and `OutgoingToken` in plaintext for every stored EI via `ExternalInitiatorResource`: [4](#0-3) [5](#0-4)  These fields are stored in plaintext in the database (`CreateExternalInitiator`) rather than hashed like `HashedSecret`: [6](#0-5) [7](#0-6) 

This is confirmed by the existing test, which asserts `GET /v2/external_initiators` returns `AccessKey` and `OutgoingToken` unmasked on every call, not just at creation: [8](#0-7) 

The broken security assumption: the application's own design intends EI management (`create`/`destroy`) to require `edit` role, but the read path that discloses the same sensitive secrets has no equivalent guard — a `view`-role user (the lowest role, intended for read-only dashboards) or `run`-role user can retrieve secrets that only `edit`+ users should be able to manage or see.

## Impact Explanation
An authenticated but low-privileged user (`view` or `run` role) can repeatedly retrieve the plaintext `AccessKey` and `OutgoingToken` for every configured external initiator via a simple authenticated GET request, with no edit/admin privilege required. This is a concrete role-bypass / secret-exfiltration issue (CWE-284/CWE-522): a `view`-role account — meant only to observe node state — can obtain credentials used to authenticate outbound calls to external initiator services, exceeding its intended read-only permission boundary. This maps to the in-scope "node API authentication or role bypass" and "key/secret exfiltration" impact categories.

## Likelihood Explanation
High feasibility once any account exists on the node with `view` or `run` role — a very low privilege bar compared to `edit`/`admin`. No special conditions are needed beyond a normal authenticated session or API token; the request is a single unauthenticated-role-check GET call, fully repeatable and requiring no host/DB access.

## Recommendation
- Wrap the `Index` route with `auth.RequiresEditRole` (or a dedicated role at least matching `Create`/`Destroy`) so only privileged users can read EI secrets: `authv2.GET("/external_initiators", auth.RequiresEditRole(paginatedRequest(eia.Index)))`.
- Additionally, avoid returning `AccessKey`/`OutgoingToken` on every list/read call; only surface them once at creation (mirroring `BridgeResource.IncomingToken`'s `omitempty`/create-only behavior), and consider hashing/encrypting `OutgoingToken`/`OutgoingSecret` at rest like `HashedSecret`.

## Proof of Concept
1. Create a node user with `view` role (`POST /v2/users` as admin, or use an existing `view`/`run` role account).
2. As that low-privilege user, authenticate and call `GET /v2/external_initiators`.
3. Observe the response includes `accessKey` and `outgoingToken` fields in plaintext for all configured external initiators, as demonstrated by the existing test assertions at `core/web/external_initiators_controller_test.go:104-126`, despite the same user being rejected with 401 by `RequiresEditRole` if they attempt `POST`/`DELETE` on the same resource.

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

**File:** core/bridges/orm.go (L227-243)
```go
// CreateExternalInitiator inserts a new external initiator
func (o *orm) CreateExternalInitiator(ctx context.Context, externalInitiator *ExternalInitiator) (err error) {
	query := `INSERT INTO external_initiators (name, url, access_key, salt, hashed_secret, outgoing_secret, outgoing_token, created_at, updated_at)
	VALUES (:name, :url, :access_key, :salt, :hashed_secret, :outgoing_secret, :outgoing_token, now(), now())
	RETURNING *
	`
	err = o.transact(ctx, false, func(tx *orm) error {
		var stmt *sqlx.NamedStmt
		stmt, err = tx.ds.PrepareNamedContext(ctx, query)
		if err != nil {
			return pkgerrors.Wrap(err, "failed to prepare named stmt")
		}
		defer stmt.Close()
		return pkgerrors.Wrap(stmt.GetContext(ctx, externalInitiator, externalInitiator), "failed to load external_initiator")
	})
	return pkgerrors.Wrap(err, "CreateExternalInitiator failed")
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
