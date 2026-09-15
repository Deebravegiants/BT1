Audit Report

## Title
Bridge and External Initiator outgoing authentication tokens stored and served in plaintext to any authenticated "View"-role user - ([File: core/bridges/bridge_type.go], [File: core/web/bridge_types_controller.go], [File: core/web/external_initiators_controller.go], [File: core/web/router.go])

## Summary
Chainlink generates `OutgoingToken` (for Bridges) and `OutgoingToken`/`OutgoingSecret` (for External Initiators) as plaintext values used by the node to authenticate itself when calling external adapters/initiators. These are persisted unencrypted and returned unredacted by the `Index`/`Show` read endpoints, which — unlike the corresponding write endpoints — are not gated behind `RequiresEditRole`/`RequiresAdminRole`, so a session with only the lowest "View" role can read every bridge's and external initiator's live outgoing credential.

## Finding Description
`bridges.NewBridgeType` generates `outgoingToken := utils.NewSecret(24)` and stores it in plaintext on the persisted `BridgeType` struct (`OutgoingToken string`), with no hashing/salting unlike `IncomingTokenHash`: [1](#0-0) [2](#0-1) 

`presenters.NewBridgeResource` copies `b.OutgoingToken` verbatim into the JSON:API resource with no redaction, and this is used by both `Index` and `Show`: [3](#0-2) [4](#0-3) 

Same pattern for `ExternalInitiator.OutgoingSecret`/`OutgoingToken`, generated in plaintext and returned via `Index`: [5](#0-4) [6](#0-5) 

Critically, the router confirms that the read routes for these resources carry **no role restriction** while the corresponding write routes do:
```go
authv2.GET("/external_initiators", paginatedRequest(eia.Index))
authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
...
authv2.GET("/bridge_types", paginatedRequest(bt.Index))
authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
authv2.GET("/bridge_types/:BridgeName", bt.Show)
authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
``` [7](#0-6) 

These GET routes only pass through `auth.Authenticate(... AuthenticateByToken, AuthenticateBySession)`, i.e., any valid session regardless of role (including `UserRoleView`) is sufficient: [8](#0-7) . This is confirmed by `auth.RequiresEditRole`, which explicitly rejects `UserRoleView` and `UserRoleRun`, showing the framework distinguishes "View" as a strictly lower-privilege tier that is deliberately excluded from write actions but was not excluded from these secret-bearing read actions: [9](#0-8) 

A test explicitly demonstrates the plaintext outgoing token being returned by the `Index` endpoint response body: [10](#0-9) 

This differs from the node's general "secrets" handling pattern (`config.SecretString`/`SecretURL`), which redacts values to `xxxxx` on marshal: [11](#0-10) . `BridgeType.OutgoingToken` and `ExternalInitiator.OutgoingToken`/`OutgoingSecret` were never migrated to this pattern.

## Impact Explanation
`OutgoingToken`/`OutgoingSecret` are live credentials the node presents to external bridge adapters/initiators. Any authenticated "View"-role user — a role explicitly designed by the codebase to be read-only/lower-privileged, as evidenced by `RequiresEditRole`/`RequiresRunRole`/`RequiresAdminRole` excluding it from other sensitive operations — can call `GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, or `GET /v2/external_initiators` and obtain plaintext outbound authentication secrets for every configured bridge/external initiator. This is a concrete privilege-boundary violation and secret exfiltration (CWE-522): a user granted only "View" access obtains credentials that would let them impersonate the node to external adapters or replay tokens against the bridge's own auth check — an in-scope impact class (secret exfiltration / role bypass).

## Likelihood Explanation
Exploitation only requires a valid "View"-role session or API token, which is a normal, expected credential tier in multi-operator Chainlink deployments and requires no additional privilege escalation. The endpoints are standard, routine listing/lookup calls (`Index`/`Show`), making this readily and repeatably reachable in any deployment that issues "View" role credentials to less-trusted operators/auditors.

## Recommendation
- Redact `OutgoingToken`/`OutgoingSecret` from `BridgeResource`/`ExternalInitiatorResource` on `Index`/`Show` responses (and the GraphQL `bridge`/`bridges` read queries); only return once, at creation time, mirroring `IncomingToken` handling.
- Wrap `OutgoingToken`/`OutgoingSecret` in `config.SecretString` or otherwise encrypt at rest.
- Gate `GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, and `GET /v2/external_initiators` behind at least `RequiresEditRole` if the raw secret must remain in the response, or strip the secret field entirely for read endpoints.

## Proof of Concept
1. As an admin, create a bridge via `POST /v2/bridge_types` — response includes `outgoingToken`.
2. Create a session/API token with `UserRoleView` (via `POST /v2/users` + role assignment, per `authv2.PATCH("/users", auth.RequiresAdminRole(uc.UpdateRole))`).
3. Using only the View-role credential, call `GET /v2/bridge_types/:BridgeName` or `GET /v2/external_initiators` — per `core/web/router.go` these routes have no `RequiresEditRole`/`RequiresAdminRole` wrapper, so the request succeeds.
4. Observe `attributes.outgoingToken` in the JSON:API response equals the plaintext token generated at creation, as already demonstrated by `TestExternalInitiatorsController_Index` asserting `eiFoo.OutgoingToken == externalInitiators[0].OutgoingToken` after an `Index` call ( [12](#0-11) ). Extending this test to authenticate with `UserRoleView` instead of a full/admin session would directly prove the privilege-boundary violation.

### Citations

**File:** core/bridges/bridge_type.go (L55-68)
```go
// BridgeType is used for external adapters and has fields for
// the name of the adapter and its URL.
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
```

**File:** core/bridges/bridge_type.go (L70-101)
```go
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
		UseConnectionManager:   btr.UseConnectionManager,
	}, &BridgeType{
		Name:                   btr.Name,
		URL:                    btr.URL,
		Confirmations:          btr.Confirmations,
		IncomingTokenHash:      hash,
		Salt:                   salt,
		OutgoingToken:          outgoingToken,
		MinimumContractPayment: btr.MinimumContractPayment,
		UseConnectionManager:   btr.UseConnectionManager,
	}, nil
```

**File:** core/web/presenters/bridges.go (L10-42)
```go
// BridgeResource represents a Bridge JSONAPI resource.
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
}
```

**File:** core/web/bridge_types_controller.go (L111-146)
```go
// Index lists Bridges, one page at a time.
func (btc *BridgeTypesController) Index(c *gin.Context, size, page, offset int) {
	ctx := c.Request.Context()
	bridges, count, err := btc.App.BridgeORM().BridgeTypes(ctx, offset, size)

	resources := make([]presenters.BridgeResource, 0, len(bridges))
	for _, bridge := range bridges {
		resources = append(resources, *presenters.NewBridgeResource(bridge))
	}

	paginatedResponse(c, "Bridges", size, page, resources, count, err)
}

// Show returns the details of a specific Bridge.
func (btc *BridgeTypesController) Show(c *gin.Context) {
	ctx := c.Request.Context()
	name := c.Param("BridgeName")

	taskType, err := bridges.ParseBridgeName(name)
	if err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	bt, err := btc.App.BridgeORM().FindBridge(ctx, taskType)
	if errors.Is(err, sql.ErrNoRows) {
		jsonAPIError(c, http.StatusNotFound, errors.New("bridge not found"))
		return
	}
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	jsonAPIResponse(c, presenters.NewBridgeResource(bt), "bridge")
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

**File:** core/web/router.go (L245-248)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
```

**File:** core/web/router.go (L263-273)
```go
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

**File:** core/web/external_initiators_controller_test.go (L105-126)
```go
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

**File:** core/store/models/secrets.go (L1-26)
```go
package models

import (
	"github.com/smartcontractkit/chainlink-common/pkg/config"
)

// Secret is a string that formats and encodes redacted, as "xxxxx".
// Deprecated
type Secret = config.SecretString

// Deprecated
func NewSecret(s string) *Secret { return config.NewSecretString(s) }

// SecretURL is a URL that formats and encodes redacted, as "xxxxx".
// Deprecated
type SecretURL = config.SecretURL

// Deprecated
func NewSecretURL(u *config.URL) *config.SecretURL { return (*config.SecretURL)(u) }

// Deprecated
func MustSecretURL(u string) *config.SecretURL {
	return NewSecretURL(config.MustParseURL(u))
}


```
