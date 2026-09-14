## Title
Unauthenticated-role disclosure of External Initiator credentials via `GET /v2/external_initiators` - (File: `core/web/router.go`)

### Summary
The `GET /v2/external_initiators` route is registered without any role-gating middleware, so any authenticated node user — including the lowest-privilege `view` role — can retrieve the `AccessKey` and `OutgoingToken` for **every** External Initiator configured on the node. This mirrors the CVE-2024-10109 pattern: a low-privilege user reaching a sensitive endpoint that discloses credential material intended to be restricted.

### Finding Description
In `v2Routes`, the External Initiators index route is mounted with no role wrapper, unlike almost every other mutating/sensitive route in the same file which is wrapped in `auth.RequiresEditRole` or `auth.RequiresAdminRole`: [1](#0-0) 

The handler, `ExternalInitiatorsController.Index`, returns every stored initiator via `presenters.NewExternalInitiatorResource`, which serializes the sensitive `AccessKey` and `OutgoingToken` fields for all initiators (not scoped to the requester): [2](#0-1) [3](#0-2) 

The RBAC test matrix confirms this route is intentionally left open to `view` role, unlike sibling `POST`/`DELETE` routes for the same resource which require `edit`: [4](#0-3) 

The `AccessKey`/`OutgoingToken` are generated as high-entropy secrets alongside a `Secret`/`OutgoingSecret` at creation time and are meant to gate External Initiator authentication and outbound webhook validation: [5](#0-4) 

While the `Secret`/`OutgoingSecret` are only returned once at creation (`Create` handler) and not stored in plaintext (`HashedSecret`), the `Index` endpoint still leaks the `AccessKey` (half of the required incoming-auth token pair) and the full `OutgoingToken` used to validate outbound requests to the initiator's remote endpoint, to any authenticated user regardless of role.

### Impact Explanation
A `view`-role user — a role intended only for read-only monitoring, per the RBAC design in `core/web/auth/auth.go` (`RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole`) — can enumerate credential material for all External Initiators on the node. This is a direct analog to the reported CVE: an under-privileged, authenticated actor reaching a sensitive endpoint and obtaining credential/secret values (`AccessKey`, `OutgoingToken`) that should be restricted to `edit`/`admin` roles, consistent with how the sibling `Create`/`Destroy` routes for the same resource are gated.

### Likelihood Explanation
High. Any authenticated session or API token — even one deliberately provisioned with only `view` access for dashboards/monitoring — can call this endpoint with no additional exploitation steps; it is a simple authenticated `GET`.

### Recommendation
Wrap `GET /v2/external_initiators` with `auth.RequiresEditRole` (or at minimum `RequiresRunRole`), matching the protection level of the `POST`/`DELETE` routes for the same resource, and consider omitting `OutgoingToken`/`AccessKey` from the paginated list response entirely, exposing them only at creation time as is already done for `Secret`/`OutgoingSecret`.

### Proof of Concept
1. Create an API user with role `view`.
2. Authenticate as that user (session or API token).
3. Call `GET /v2/external_initiators` — the response includes `accessKey` and `outgoingToken` for every configured External Initiator, e.g.:
```
GET /v2/external_initiators
Authorization: <view-role session/token>

{
  "data": [{
    "type": "externalInitiators",
    "id": "1",
    "attributes": {
      "name": "bitcoin",
      "url": "http://example.com",
      "accessKey": "<leaked>",
      "outgoingToken": "<leaked>"
    }
  }]
}
```
Confirmed by the RBAC route matrix marking this route `viewOnlyAllowed: true`: [6](#0-5)

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

**File:** core/web/auth/auth_test.go (L224-226)
```go
	{"GET", "/v2/external_initiators", true, true, true},
	{"POST", "/v2/external_initiators", false, false, true},
	{"DELETE", "/v2/external_initiators/MOCK", false, false, true},
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
