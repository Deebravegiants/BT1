### Title
Low-privileged (`view`) API users can read live External Initiator secrets via `GET /v2/external_initiators` - ([File: core/web/external_initiators_controller.go])

### Summary
The `ExternalInitiatorsController.Index` handler returns the `AccessKey` and `OutgoingToken` for every configured External Initiator to any authenticated node API user, including users with only the `view` role (the lowest permission tier). This is the same bug class as CVE-2022-36919: a low-privileged, read-only actor obtains credential material through an API endpoint whose permission check does not gate the sensitive fields being returned.

### Finding Description
`ExternalInitiatorsController.Index` builds a `presenters.ExternalInitiatorResource` for every stored `bridges.ExternalInitiator` and serializes it in the paginated response: [1](#0-0) 

`ExternalInitiatorResource` includes `AccessKey` and `OutgoingToken` as first-class JSON fields (not omitted or redacted): [2](#0-1) 

`OutgoingToken` is a live secret generated at creation time (`utils.NewSecret(...)`) and stored/used to authenticate outbound webhook calls the node makes to the external initiator, alongside `OutgoingSecret`: [3](#0-2) 

The RBAC integration test (`routesRolesMap`) explicitly documents and asserts that `GET /v2/external_initiators` is allowed for `viewOnly`, `editMinimal`, and `Edit` roles (i.e., not admin-only), confirming the `view` role — the read-only equivalent of Jenkins' `Overall/Read` — can hit this endpoint successfully: [4](#0-3) 

Unlike the Jenkins Coverity Plugin bug, which only leaked *credential IDs* (opaque references), this endpoint leaks the actual `AccessKey` and `OutgoingToken` values in plaintext to any `view`-role user — a strictly stronger exposure of the same "missing/insufficient permission gating on credential enumeration" bug class.

### Impact Explanation
A `view`-role API user (intended for read-only monitoring, not secret access) can retrieve the `AccessKey`/`OutgoingToken` of every External Initiator configured on the node. `AccessKey`/`OutgoingToken` are used to authenticate requests to/from the node's external-initiator integrations; disclosure allows a low-privileged internal actor to impersonate or interfere with those integrations, going beyond simple enumeration into direct credential/secret disclosure.

### Likelihood Explanation
Any user who has been granted the lowest `view` role on the node's API can trigger this simply by calling `GET /v2/external_initiators` — no special conditions, timing, or race required, and the route is explicitly permitted for that role per the RBAC test matrix.

### Recommendation
Redact `AccessKey` and `OutgoingToken`/`OutgoingSecret` from `ExternalInitiatorResource` responses returned by `Index` (list) for non-admin/non-edit roles, or require an elevated role (e.g., `admin`) to access `GET /v2/external_initiators`, mirroring how secrets are only shown once on `Create`. Ensure any listing surface for credential-bearing resources returns only non-sensitive identifiers (e.g., `name`, `id`) by default.

### Proof of Concept
1. Create a Chainlink node API user with role `view`.
2. As an admin, create an External Initiator (`POST /v2/external_initiators`) — this returns and stores an `AccessKey`/`OutgoingToken`.
3. Authenticate as the `view` user and call `GET /v2/external_initiators`.
4. Observe the response includes each initiator's `accessKey` and `outgoingToken` in plaintext, per `presenters.ExternalInitiatorResource` ( [5](#0-4) ), despite the caller only holding read-only privileges.

### Citations

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

**File:** core/web/auth/auth_test.go (L224-224)
```go
	{"GET", "/v2/external_initiators", true, true, true},
```
