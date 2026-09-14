## Finding: External initiator `OutgoingToken` secret disclosed to View-role users via `GET /v2/external_initiators`

### Title
Read-only ("View" role) authenticated user can retrieve External Initiator `OutgoingToken` secret via `GET /v2/external_initiators` - (File: `core/web/external_initiators_controller.go`)

### Summary
The `GET /v2/external_initiators` endpoint is registered without any role gate and returns every stored External Initiator's `OutgoingToken` in cleartext, so the lowest-privilege authenticated node user (`UserRoleView`) can read this secret credential, which is otherwise meant to be used only by the node to authenticate itself when calling back into the external initiator's webhook.

### Finding Description
The route is registered with no `auth.RequiresEditRole`/`RequiresRunRole`/`RequiresAdminRole` wrapper, unlike almost every other mutating or sensitive endpoint on the same router group: [1](#0-0) 

The handler builds its response from `bridges.ExternalInitiator` records pulled straight from the DB and converts them with `NewExternalInitiatorResource`: [2](#0-1) 

That presenter explicitly serializes the `OutgoingToken` field into the JSON response: [3](#0-2) 

`OutgoingToken` is a generated secret (`utils.NewSecret(utils.DefaultSecretSize)`) created alongside `OutgoingSecret` when the initiator is registered, intended to authenticate the node's outbound calls to the external initiator: [4](#0-3) 

The project's own RBAC test suite confirms `GET /v2/external_initiators` is reachable by the `view` role (`viewOnlyAllowed: true`), i.e. the weakest role in the system: [5](#0-4) [6](#0-5) 

This is directly analogous to CVE-2020-2131: a secret that should be protected (there, SCM passwords in `config.xml`; here, the `OutgoingToken`) is exposed to a low-privilege, "extended read"-equivalent actor (`UserRoleView`) through a normal, unprivileged API path rather than requiring elevated access.

### Impact Explanation
Any authenticated node user with only View role — the role intended for dashboards/monitoring/read-only access — can enumerate all configured external initiators and obtain their `OutgoingToken`. Depending on how the receiving external initiator validates this token on inbound requests it accepts from the Chainlink node, disclosure of this token could allow a low-privileged user to impersonate the node when calling the initiator's endpoint, or otherwise misuse a credential that should be confined to Edit/Admin-level operators who manage external initiators.

### Likelihood Explanation
Likelihood is high for exploitation once the vulnerability class is understood: no special conditions are required beyond having any valid session/API token with the lowest role, and the endpoint is a simple unauthenticated-by-role `GET` that any dashboard or automated read-only integration would call.

### Recommendation
Wrap `GET /v2/external_initiators` with at least `auth.RequiresEditRole` (matching the `POST`/`DELETE` external-initiator routes), and/or strip `OutgoingToken` (and any other secret) from `ExternalInitiatorResource`, returning it only once at creation time via `ExternalInitiatorAuthentication` as is already done in `Create`.

### Proof of Concept
1. Create a user with `UserRoleView` and an External Initiator (via an Edit/Admin user) so an `OutgoingToken` exists.
2. As the View-role user, call:
   `GET /v2/external_initiators`
   with a valid session/API token.
3. Observe the JSON response includes each initiator's `outgoingToken` field in cleartext, confirmed by the resource shape returned from `NewExternalInitiatorResource`. [3](#0-2)

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

**File:** core/bridges/external_initiator.go (L21-56)
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
```

**File:** core/web/auth/auth_test.go (L224-224)
```go
	{"GET", "/v2/external_initiators", true, true, true},
```

**File:** core/sessions/user.go (L85-98)
```go
// GetUserRole is the single point of logic for mapping role string to UserRole
func GetUserRole(role string) (UserRole, error) {
	if role == string(UserRoleAdmin) {
		return UserRoleAdmin, nil
	}
	if role == string(UserRoleEdit) {
		return UserRoleEdit, nil
	}
	if role == string(UserRoleRun) {
		return UserRoleRun, nil
	}
	if role == string(UserRoleView) {
		return UserRoleView, nil
	}
```
