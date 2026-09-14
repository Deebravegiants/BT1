### Title
Unnecessarily broad read access exposes External Initiator `OutgoingToken` secret to any authenticated node role - (File: core/web/router.go)

### Summary
The audited UMA `BridgePool` issue is about a contract holding administrative capabilities (mint/burn) it does not need, exposing an unnecessary attack surface. The Chainlink node analog is the inverse but structurally identical problem: an endpoint is granted broader-than-necessary access, letting a low-privileged (view/run-role) authenticated user read a secret that should only be reachable by edit/admin-tier operators.

### Finding Description
The `GET /v2/external_initiators` route is registered without any role gate, unlike the sibling `POST`/`DELETE` routes on the same resource which are wrapped in `auth.RequiresEditRole`: [1](#0-0) 

`ExternalInitiatorsController.Index` returns every external initiator record via `presenters.NewExternalInitiatorResource`, which includes the `OutgoingToken` field: [2](#0-1) [3](#0-2) 

`OutgoingToken` is a generated secret (`utils.NewSecret(utils.DefaultSecretSize)`) created at `ExternalInitiator` creation time: [4](#0-3) 

Because the `Index` handler is mounted under the generic authenticated group (`authv2`, accepting `AuthenticateByToken` or `AuthenticateBySession`) with no `RequiresEditRole`/`RequiresAdminRole` wrapper, any authenticated node user — including the lowest `view` role — can list this secret for every configured external initiator. This mirrors the audit's root cause: a capability (here, read access to sensitive credential material) is granted more broadly than the functionality actually requires, since only edit/admin operators manage external initiators (`Create`/`Destroy` require edit role).

### Impact Explanation
`OutgoingToken` is a bearer secret meant to gate initiator-facing functionality tied to the job-run pipeline. Exposing it to any authenticated (even read-only "view" role) API/session user violates the principle of least privilege enforced everywhere else on this resource (`Create`/`Destroy` are edit-gated) and on comparable resources (`/v2/users`, `/v2/transfers` require admin). A low-privilege credential holder could retrieve secrets belonging to integrations they should not be able to see or influence, undermining the role-segregation model the rest of the API enforces.

### Likelihood Explanation
Likelihood is moderate-to-high in any deployment where operators create accounts with `view` or `run` roles for auditors, monitoring, or automation. No user interaction beyond a normal authenticated API call is required, and the exposure occurs on every call to a legitimate, exposed endpoint (`GET /v2/external_initiators`) with no special conditions.

### Recommendation
Require at least `RequiresEditRole` (consistent with `Create`/`Destroy` on the same resource) on `GET /v2/external_initiators`, or strip `OutgoingToken`/other secrets from `ExternalInitiatorResource` for non-privileged callers, so unprivileged/read-only roles cannot retrieve initiator secrets they have no operational need to access.

### Proof of Concept
1. Create/obtain a node API user with role `view` (lowest privilege) or an API token for such a user via `auth.AuthenticateByToken`.
2. Have an admin/edit user create an external initiator via `POST /v2/external_initiators`, which generates and stores an `OutgoingToken`.
3. As the `view`-role user, call `GET /v2/external_initiators` (only wrapped by `paginatedRequest`, no role check per `core/web/router.go` lines 263-266).
4. Observe the JSON response includes `outgoingToken` for every initiator, per `presenters.NewExternalInitiatorResource` — a secret the `view` role should not be entitled to read.

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
