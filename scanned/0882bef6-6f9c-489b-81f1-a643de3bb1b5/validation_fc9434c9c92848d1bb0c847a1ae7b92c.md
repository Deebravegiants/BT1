### Title
Unauthenticated-role external initiator credential disclosure via missing role check on GET /v2/external_initiators - (File: core/web/router.go)

### Summary
The Jenkins GitLab Logo Plugin CVE describes a credential-disclosure bug class where a secret is accessible to a user who should not have privilege to view it. In this codebase, the `GET /v2/external_initiators` endpoint returns the `OutgoingToken` credential for every registered External Initiator to any authenticated user, regardless of role, while the sibling `Create`/`Destroy` routes on the same resource are explicitly gated behind `auth.RequiresEditRole`.

### Finding Description
In `core/web/router.go`, the external initiators routes are registered as: [1](#0-0) 

`eia.Index` has no role guard, whereas `Create` and `Destroy` require `RequiresEditRole`. Any principal that can pass the generic `authv2` group authentication (session cookie or API token, which covers low-privilege roles such as "View" or "Run", not just Edit/Admin) can call `Index` and receive the full paginated list of `ExternalInitiatorResource` entries.

`ExternalInitiatorsController.Index` fetches all initiators and serializes them via `presenters.NewExternalInitiatorResource`: [2](#0-1) 

The presenter includes the `OutgoingToken` field in the JSON response: [3](#0-2) 

`OutgoingToken` is a real secret: it is generated with `utils.NewSecret` at initiator creation time and used by the node to authenticate itself when calling back out to the initiator's webhook: [4](#0-3) 

It is stored as plaintext in the `external_initiators` table (`outgoing_token` column) with no application-side encryption: [5](#0-4) 

Unlike the config `Secrets` type, which redacts values in `TOMLString()`/`SecretString`, the JSON API presenter for this resource does not redact `OutgoingToken`, and the `Index` route has no role restriction to compensate.

### Impact Explanation
Any authenticated node user — including accounts intended only for the "View" (read-only) or "Run" role, not just "Edit"/"Admin" — can retrieve every external initiator's `OutgoingToken`. Because this token is presented by the node itself when calling the initiator's `URL` (see `NewExternalInitiator`/`OutgoingToken` usage), possession of it lets a low-privileged actor impersonate the Chainlink node to the external initiator service, or replay/forge outgoing callbacks the initiator would otherwise trust as originating from the node. This is a concrete secret-disclosure / privilege-boundary bypass, matching CWE-522 (credentials accessible to users who should not have that access), directly analogous to the Jenkins plugin issue where secrets in configuration were viewable by lower-privileged filesystem users.

### Likelihood Explanation
Exploitation requires only a valid low-privilege authenticated session or API token for the node (any role satisfying the generic `authv2` auth middleware) and a single unauthenticated-role GET request; no additional conditions (feature flags aside from `ExternalInitiatorsEnabled` for creation, which is unrelated to reading) are needed to read `Index`. Given that External Initiators are a documented, actively-used feature (webhook/job-run triggering), and that view/run-level API keys are commonly issued to less-trusted integrations/services, likelihood is not negligible, but this does require the attacker to already hold *some* authenticated credential on the node (a "View"-only key), so it is not remotely unauthenticated.

### Recommendation
Add a role check to the `Index` route consistent with `Create`/`Destroy`, e.g. require `auth.RequiresEditRole` (or a dedicated read scope) on `authv2.GET("/external_initiators", ...)`, and/or strip `OutgoingToken`/`OutgoingSecret`-derived fields from the list presenter (`presenters.ExternalInitiatorResource`) so that only the creation response (`ExternalInitiatorAuthentication`, returned once at creation time) ever discloses the token.

### Proof of Concept
1. Obtain a node account/API key provisioned with the lowest role (`clsessions.UserRoleView` or `UserRoleRun`), which passes the generic `authv2` authentication group in `core/web/router.go` line 245-248.
2. Send `GET /v2/external_initiators` with that low-privilege session/token.
3. Observe the JSON response contains `outgoingToken` for every configured external initiator (per `presenters.ExternalInitiatorResource.OutgoingToken`), even though the account has no `Edit`/`Admin` role and cannot itself create/delete initiators.
4. Use the disclosed `OutgoingToken` to impersonate the node when calling the initiator's registered `URL`. [6](#0-5)

### Citations

**File:** core/web/router.go (L245-266)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
	{
		uc := UserController{app}
		authv2.GET("/users", auth.RequiresAdminRole(uc.Index))
		authv2.POST("/users", auth.RequiresAdminRole(uc.Create))
		authv2.PATCH("/users", auth.RequiresAdminRole(uc.UpdateRole))
		authv2.DELETE("/users/:email", auth.RequiresAdminRole(uc.Delete))
		authv2.PATCH("/user/password", uc.UpdatePassword)
		authv2.POST("/user/token", uc.NewAPIToken)
		authv2.POST("/user/token/delete", uc.DeleteAPIToken)

		wa := NewWebAuthnController(app)
		authv2.GET("/enroll_webauthn", wa.BeginRegistration)
		authv2.POST("/enroll_webauthn", wa.FinishRegistration)

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

**File:** core/store/migrate/migrations/0001_initial.sql (L483-495)
```sql
CREATE TABLE public.external_initiators (
    id bigint NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    deleted_at timestamp with time zone,
    name text NOT NULL,
    url text,
    access_key text NOT NULL,
    salt text NOT NULL,
    hashed_secret text NOT NULL,
    outgoing_secret text NOT NULL,
    outgoing_token text NOT NULL
);
```
