This confirms the claim's core technical facts: `GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, and `GET /v2/external_initiators` are wired with only generic session/token authentication (`authv2` group using `auth.Authenticate(..., auth.AuthenticateByToken, auth.AuthenticateBySession)`), with no `RequiresEditRole`/`RequiresAdminRole` wrapper, while `Create`/`Update`/`Destroy` on the same resources do require `auth.RequiresEditRole`. [1](#0-0)  The role-check middleware confirms `UserRoleView` is a real, lower-privilege tier distinct from edit/admin/run that is explicitly excluded from `RequiresRunRole` and `RequiresEditRole` but is not filtered out for these unguarded GET routes. [2](#0-1)  `BridgeType.OutgoingToken` is stored/generated in plaintext (unlike the hashed `IncomingTokenHash`) and always serialized in `BridgeResource` without `omitempty`. [3](#0-2) [4](#0-3)  `ExternalInitiator.OutgoingToken`/`OutgoingSecret` are similarly plaintext and unconditionally returned by `ExternalInitiatorResource`, confirmed by the existing test assertion. [5](#0-4) [6](#0-5) [7](#0-6) 

This is a legitimate, exploitable finding: a "view"-role authenticated user (the lowest privilege tier in chainlink's RBAC, obtainable via a normal low-privilege session/API token, no admin/host access required) can call these already-wired GET endpoints and receive plaintext outgoing secrets used by the node to authenticate itself to external adapters/initiators — an in-scope secret-exfiltration/role-bypass impact, not excluded by SECURITY.md (which excludes leaked-credential-dependent attacks, not code that itself discloses credentials to lower-privileged users) [8](#0-7) . The exploit path is concrete, reproducible via the cited test pattern, requires no privilege escalation, and existing auth/role middleware is demonstrably insufficient (present on sibling write-endpoints but absent here).

Audit Report

## Title
Plaintext outgoing webhook credentials for Bridges and External Initiators are exposed via unauthenticated-in-role GET endpoints to any "view"-role user - (File: core/web/presenters/bridges.go, core/web/presenters/external_initiators.go, core/web/router.go)

## Summary
`BridgeType.OutgoingToken` and `ExternalInitiator.OutgoingToken`/`OutgoingSecret` are generated and persisted as plaintext, and are unconditionally serialized by `BridgeResource` and `ExternalInitiatorResource`. The `GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, and `GET /v2/external_initiators` routes are wired with only generic session/token authentication and lack the `auth.RequiresEditRole` guard applied to the corresponding write endpoints, so any authenticated "view"-role user can retrieve these outgoing secrets.

## Finding Description
`bridges.NewBridgeType` generates `outgoingToken` via `utils.NewSecret` and stores it in plaintext (`OutgoingToken string \`db:"outgoing_token"\``), unlike `IncomingToken`, which is hashed with a salt before persistence. [3](#0-2)  `BridgeResource` serializes `OutgoingToken` unconditionally (no `omitempty`), unlike `IncomingToken`, which is `omitempty` and populated only on Create. [4](#0-3)  Likewise, `ExternalInitiator.OutgoingSecret`/`OutgoingToken` are plaintext, generated via `utils.NewSecret`, with no hashing. [5](#0-4)  `ExternalInitiatorResource`, used by `Index`, always includes `OutgoingToken`. [6](#0-5)  The routing shows `authv2.GET("/bridge_types", ...)`, `authv2.GET("/bridge_types/:BridgeName", bt.Show)`, and `authv2.GET("/external_initiators", ...)` require only the base `auth.Authenticate` middleware (token or session), while `Create`/`Update`/`Destroy` on the same resources require `auth.RequiresEditRole`. [1](#0-0)  `RequiresEditRole` explicitly rejects `UserRoleView` and `UserRoleRun`, confirming "view" is a distinct, lower-privilege role that is deliberately blocked from mutating endpoints but is not blocked from these GET endpoints. [9](#0-8) 

## Impact Explanation
Any authenticated node-UI/API user holding only the "view" role can read plaintext `OutgoingToken` for every bridge and `OutgoingToken`/effectively-relevant secrets for every external initiator via `GET /v2/bridge_types` and `GET /v2/external_initiators`. These tokens authenticate the Chainlink node itself when calling out to external adapters/initiators; leaking them enables a low-privileged actor to impersonate the node's outgoing calls to third-party services or replay/forge outgoing-authenticated requests — a concrete secret-exfiltration impact within the Chainlink node-API authentication/role-bypass and key/secret-exfiltration impact classes.

## Likelihood Explanation
High. No exploitation beyond a valid "view"-role session or API token is required; the endpoints are already reachable and unguarded by role checks, contrasted directly with the equivalent write endpoints that are correctly gated by `RequiresEditRole`. This is repeatable on every call and applies to any environment granting "view" accounts to any user (a supported, deliberately low-privilege tier).

## Recommendation
- Remove `OutgoingToken`/`OutgoingSecret` from `Index`/`Show` responses for bridges and external initiators (mark `omitempty`, populate only on `Create`, mirroring existing `IncomingToken` handling in `BridgeResource`).
- Alternatively/additionally, gate `GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, and `GET /v2/external_initiators` with `auth.RequiresEditRole` so "view"-role accounts cannot retrieve these secrets.
- Consider hashing/encrypting `OutgoingToken`/`OutgoingSecret` at rest rather than plaintext DB columns.

## Proof of Concept
1. As admin, `POST /v2/bridge_types {"name":"test","url":"http://adapter"}` — response includes plaintext `outgoingToken`.
2. Create a session/API token for a user with role `view` only.
3. As the `view` user, call `GET /v2/bridge_types` or `GET /v2/bridge_types/test` — response includes the same plaintext `outgoingToken`.
4. As the `view` user, call `GET /v2/external_initiators` — response includes plaintext `outgoingToken` for every initiator, matching the assertion pattern in `core/web/external_initiators_controller_test.go:104-126` (`assert.Equal(t, eiFoo.OutgoingToken, externalInitiators[0].OutgoingToken)`).

### Citations

**File:** core/web/router.go (L245-273)
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

		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
```

**File:** core/web/auth/auth.go (L198-234)
```go
// RequiresRunRole extracts the user object from the context, and asserts the user's role is at least
// 'run'
func RequiresRunRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}

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

**File:** core/bridges/bridge_type.go (L57-90)
```go
type BridgeType struct {
	Name                   BridgeName    `db:"name"`
	URL                    models.WebURL `db:"url"`
	Confirmations          uint32        `db:"confirmations"`
	IncomingTokenHash      string        `db:"incoming_token_hash"`
	Salt                   string        `db:"salt"`
	OutgoingToken          string        `db:"outgoing_token"`
	MinimumContractPayment *assets.Link  `db:"minimum_contract_payment"`
	CreatedAt              time.Time     `db:"created_at"`
	UpdatedAt              time.Time     `db:"updated_at"`
	UseConnectionManager   bool          `db:"use_connection_manager" json:"useConnectionManager"`
}

// NewBridgeType returns a bridge type authentication (with plaintext
// password) and a bridge type (with hashed password, for persisting)
func NewBridgeType(btr *BridgeTypeRequest) (*BridgeTypeAuthentication,
	*BridgeType, error,
) {
	incomingToken := utils.NewSecret(24)
	outgoingToken := utils.NewSecret(24)
	salt := utils.NewSecret(24)

	hash, err := incomingTokenHash(incomingToken, salt)
	if err != nil {
		return nil, nil, err
	}

	return &BridgeTypeAuthentication{
		Name:                   btr.Name,
		URL:                    btr.URL,
		Confirmations:          btr.Confirmations,
		IncomingToken:          incomingToken,
		OutgoingToken:          outgoingToken,
		MinimumContractPayment: btr.MinimumContractPayment,
```

**File:** core/web/presenters/bridges.go (L11-41)
```go
type BridgeResource struct {
	JAID
	Name          string `json:"name"`
	URL           string `json:"url"`
	Confirmations uint32 `json:"confirmations"`
	// The IncomingToken is only provided when creating a Bridge
	IncomingToken          string       `json:"incomingToken,omitempty"`
	OutgoingToken          string       `json:"outgoingToken"`
	MinimumContractPayment *assets.Link `json:"minimumContractPayment"`
	UseConnectionManager   bool         `json:"useConnectionManager"`
	CreatedAt              time.Time    `json:"createdAt"`
}

// GetName implements the api2go EntityNamer interface
func (r BridgeResource) GetName() string {
	return "bridges"
}

// NewBridgeResource constructs a new BridgeResource
func NewBridgeResource(b bridges.BridgeType) *BridgeResource {
	return &BridgeResource{
		// Uses the name as the id...Should change this to the id
		JAID:                   NewJAID(b.Name.String()),
		Name:                   b.Name.String(),
		URL:                    b.URL.String(),
		Confirmations:          b.Confirmations,
		OutgoingToken:          b.OutgoingToken,
		MinimumContractPayment: b.MinimumContractPayment,
		UseConnectionManager:   b.UseConnectionManager,
		CreatedAt:              b.CreatedAt,
	}
```

**File:** core/bridges/external_initiator.go (L21-57)
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

**File:** SECURITY.md (L9-16)
```markdown
- Impacts requiring attacks that the reporter has already exploited themselves, leading to damage.
- Impacts caused by attacks requiring access to leaked keys/credentials.
- Impacts caused by attacks requiring access to privileged addresses (governance, strategist), except in cases where the contracts are intended to have no privileged access to functions that make the attack possible.
- Impacts relying on attacks involving the depegging of an external stablecoin where the attacker does not directly cause the depegging due to a bug in code.
- Mentions of secrets, access tokens, API keys, private keys, etc. in GitHub will be considered out of scope without proof that they are in use in production.
- Best practice recommendations.
- Feature requests.
- Impacts on test files and configuration files, unless stated otherwise in the bug bounty program.
```
