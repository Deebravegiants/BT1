The `GET /v2/external_initiators` route is registered without any role-based middleware, unlike every other sensitive external-initiator route.

### Title
Unauthenticated-role disclosure of External Initiator `outgoingToken` via `GET /v2/external_initiators` - (File: core/web/router.go)

### Summary
The `/v2/external_initiators` listing endpoint is mounted without any role gate, while `POST`/`DELETE` on the same resource require `RequiresEditRole`. Any authenticated user, even one with the lowest-privilege `view` role, can call this endpoint and receive each External Initiator's `OutgoingToken` in the response body.

### Finding Description
In `v2Routes`, the route wiring for external initiators is: [1](#0-0) 

Only `Index` (GET, listing) is left unguarded by any `auth.RequiresXRole` wrapper — `Create` and `Destroy` both require `auth.RequiresEditRole`. Any user authenticated via session or API token (including `view`-role users) can call GET and hit `ExternalInitiatorsController.Index`: [2](#0-1) 

That handler serializes every stored `ExternalInitiator` via `presenters.NewExternalInitiatorResource`, which includes the `OutgoingToken` field in the JSON response: [3](#0-2) 

The `OutgoingToken` (together with `OutgoingSecret`, not exposed here but conceptually paired) is the credential the Chainlink node uses to authenticate to the external initiator when notifying it of job triggers/results (see `NewExternalInitiator` generating `OutgoingToken`/`OutgoingSecret` at creation time): [4](#0-3) 

This is a secret-redaction/authorization gap: a low-privilege (`view`) authenticated principal can read a secret token intended to be scoped to admin/edit-level operators managing external initiators.

### Impact Explanation
Disclosure of `OutgoingToken` lets a low-privileged, authenticated attacker impersonate the Chainlink node when communicating with the configured external initiator endpoint (`ExternalInitiator.URL`), i.e., forge "job triggered/complete" callbacks that the external initiator would otherwise trust as coming from the node. Depending on what the external initiator does with that token (e.g., grant access to trigger job runs back into the node, or perform actions on the EI's own system), this is an authentication/impersonation-token disclosure to an unprivileged internal actor — a direct violation of the role-based access model the rest of the external-initiators routes enforce.

### Likelihood Explanation
High likelihood: any user who can authenticate to the node's API — even the lowest `view` role, or a compromised low-privilege API token — can trivially call `GET /v2/external_initiators` and receive the secret in the JSON response. No special conditions or race are required.

### Recommendation
Add the missing role check to match the access-control pattern used for the other external-initiator routes, e.g.:
```go
authv2.GET("/external_initiators", auth.RequiresEditRole(paginatedRequest(eia.Index)))
```
or, if `view` role should still be able to list initiators, exclude `OutgoingToken`/`OutgoingSecret` from `ExternalInitiatorResource` and only return them once, at creation time (as is already done via `ExternalInitiatorAuthentication` in `Create`).

### Proof of Concept
1. Create a user with role `view` (or use a `view`-scoped API token).
2. Authenticate and call `GET /v2/external_initiators`.
3. Observe the JSON response includes `outgoingToken` for every registered external initiator, even though the same low-privilege user is rejected (`403 Forbidden`) when calling `POST /v2/external_initiators` or `DELETE /v2/external_initiators/:Name` due to `auth.RequiresEditRole` on those routes — demonstrating the inconsistent/missing access control on the `Index` (list) route.

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
