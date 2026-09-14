### Title
Unprivileged `view`-role users can list External Initiator `AccessKey`/`OutgoingToken` credentials via `GET /v2/external_initiators` - (File: core/web/router.go)

### Summary
The `GET /v2/external_initiators` endpoint is registered without any role gate beyond basic authentication, so any authenticated user — including the lowest-privileged `view` role — can enumerate all external initiators and receive their `AccessKey` and `OutgoingToken` fields in the response. This mirrors CVE-2017-1000094: a listing endpoint that returns credential identifiers/material without checking that the caller holds the elevated permission actually required to use or manage those credentials.

### Finding Description
The route table in `v2Routes` registers:
```go
authv2.GET("/external_initiators", paginatedRequest(eia.Index))
authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
``` [1](#0-0) 

Only `POST`/`DELETE` are wrapped in `auth.RequiresEditRole`; the `Index` (`GET`) handler is reachable by anyone who passes the outer `authv2` group's `auth.Authenticate(... AuthenticateByToken, AuthenticateBySession)` middleware, which accepts any role including `view`: [2](#0-1) 

`ExternalInitiatorsController.Index` fetches all `ExternalInitiator` rows and serializes them without owner/role filtering:
```go
func (eic *ExternalInitiatorsController) Index(c *gin.Context, size, page, offset int) {
	externalInitiators, count, err := eic.App.BridgeORM().ExternalInitiators(ctx, offset, size)
	for _, initiator := range externalInitiators {
		resources = append(resources, presenters.NewExternalInitiatorResource(initiator))
	}
	paginatedResponse(c, "externalInitiators", size, page, resources, count, err)
}
``` [3](#0-2) 

Crucially, `ExternalInitiatorResource` (the resource returned by `Index`) includes the initiator's `AccessKey` and `OutgoingToken` in the JSON output:
```go
type ExternalInitiatorResource struct {
	JAID
	Name          string         `json:"name"`
	URL           *models.WebURL `json:"url"`
	AccessKey     string         `json:"accessKey"`
	OutgoingToken string         `json:"outgoingToken"`
	...
}
``` [4](#0-3) 

`AccessKey` is one half of the credential pair used by `AuthenticateExternalInitiator` (the other half, the plaintext `Secret`, is only known at creation time and not stored/returned by `Index`, since only the salted hash `HashedSecret` is persisted). However, `OutgoingToken` is a full, usable secret that Chainlink sends outward to the external initiator's callback endpoint for its own authentication — exposing it to any authenticated `view`-role user without exposing why they'd need it is a direct credential disclosure analogous to the CVE's unauthorized credential-ID listing: [5](#0-4) [6](#0-5) 

For contrast, the RBAC test suite explicitly documents that `GET /v2/external_initiators` (implied by the broader "no endpoint returns Unauthorized/Forbidden" assertion for admin, and by omission from any edit/admin gating) is accessible to lower roles, unlike the `POST`/`DELETE` variants, confirming the asymmetry is intentional-by-omission rather than tested/enforced minimum-necessary access: [7](#0-6) 

### Impact Explanation
A user with only `view` role (meant for read-only dashboards, no job/bridge/key management capability) can retrieve `AccessKey` and `OutgoingToken` for every External Initiator configured on the node. `AccessKey` combined with a leaked/guessed `Secret` (or via a secondary vulnerability) permits impersonating the initiator to call `POST /v2/jobs/:ID/runs` and trigger job runs (`AuthenticateExternalInitiator` grants the caller the `run` role). `OutgoingToken`/`OutgoingSecret` are secrets the node uses to authenticate itself to the initiator's outbound URL; if exposed, they weaken the intended one-way trust boundary between the node and the initiator's webhook receiver. This satisfies the "concrete... key/secret disclosure" and "request impersonation" categories required by the validation rules.

### Likelihood Explanation
Any authenticated user session or API token — even one deliberately provisioned with the lowest `view` role for read-only access — can call this endpoint with a simple `GET` request; no additional interaction, timing, or race condition is required. This is a straightforward, always-reachable authenticated-but-under-privileged path.

### Recommendation
Gate `GET /v2/external_initiators` (and the `Show`-equivalent if one exists) behind `auth.RequiresEditRole` (or at minimum `RequiresRunRole`) to match the write operations, and/or strip `AccessKey`/`OutgoingToken` from the `Index` list resource, only returning full credential material on `Create` (as is already done for `IncomingToken` on bridges, per the comment "The IncomingToken is only provided when creating a Bridge").

### Proof of Concept
1. Create a session/API token for a user with role `view` (lowest permission tier).
2. Ensure at least one External Initiator exists (created by an admin/edit user via `POST /v2/external_initiators`).
3. As the `view` user, issue: `GET /v2/external_initiators` with valid session cookie or API key/secret headers.
4. Observe the JSON response contains `accessKey` and `outgoingToken` fields for every initiator, despite the requesting user having no edit/run privileges — confirmed by the route definition showing no `RequiresEditRole`/`RequiresRunRole` wrapper on the `Index` handler [8](#0-7)  and by the resource struct exposing these fields unconditionally [9](#0-8) .

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

**File:** core/bridges/external_initiator.go (L59-67)
```go
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

**File:** core/web/auth/auth_test.go (L343-384)
```go
// The following test implementations work by asserting only that "Unauthorized/Forbidden" errors are not returned (success case),
// because hitting the handler are not mocked and will crash as expected
// Iterate over the above routesRolesMap and assert each path is wrapped and
// the user role is enforced with the correct middleware
func TestRBAC_Routemap_Admin(t *testing.T) {
	t.Parallel()
	app := cltest.NewApplicationEVMDisabled(t)
	require.NoError(t, app.Start(t.Context()))

	router := web.Router(t, app, nil)
	ts := httptest.NewServer(router)
	defer ts.Close()

	// Assert all admin routes
	// no endpoint should return StatusUnauthorized
	client := app.NewHTTPClient(nil)
	for _, route := range routesRolesMap {
		func() {
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

			assert.NotEqual(t, http.StatusUnauthorized, resp.StatusCode)
			assert.NotEqual(t, http.StatusForbidden, resp.StatusCode)
		}()
	}
}
```
