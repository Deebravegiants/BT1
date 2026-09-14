### Title
Missing Role-Based Access Control on External Initiator Listing Endpoint Exposes Access Keys and Outgoing Tokens - ([File: core/web/router.go])

### Summary
The bug class in the report — a privileged operation (`recoverERC20`) missing its `onlyOwner` restriction, allowing an unauthorized actor to perform an operation that should be admin-gated — has a direct analog in the Chainlink node's HTTP API: the `GET /v2/external_initiators` route is registered without any role gate, while the sibling `POST`/`DELETE` routes on the same resource are explicitly restricted to `edit` role and above.

### Finding Description
In `core/web/router.go`, the External Initiator routes are registered as: [1](#0-0) 

```go
eia := ExternalInitiatorsController{app}
authv2.GET("/external_initiators", paginatedRequest(eia.Index))
authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
```

`Create` and `Destroy` are wrapped in `auth.RequiresEditRole`, but `Index` is not wrapped in any role-check middleware at all. It only inherits the generic `authv2` group's authentication requirement (`AuthenticateByToken` / `AuthenticateBySession`), meaning any authenticated user — including one with the lowest privilege `view` role — can call this endpoint [2](#0-1) .

`Index` returns every registered external initiator through `presenters.NewExternalInitiatorResource`, which serializes the initiator's `AccessKey` and `OutgoingToken`: [3](#0-2) 

```go
type ExternalInitiatorResource struct {
	JAID
	Name          string         `json:"name"`
	URL           *models.WebURL `json:"url"`
	AccessKey     string         `json:"accessKey"`
	OutgoingToken string         `json:"outgoingToken"`
	...
}
```

`AccessKey` is one of the two credentials (`AccessKey` + `Secret`) used to authenticate as an external initiator via `AuthenticateExternalInitiator` middleware, which grants the caller the `run` role sufficient to trigger job runs [4](#0-3) . `OutgoingToken` is the credential the node uses to authenticate itself when calling back out to the external initiator's webhook, per `bridges.ExternalInitiator` [5](#0-4) .

While the `Secret` (hashed and salted) is not returned by `Index`, disclosure of `AccessKey` and `OutgoingToken` to unprivileged `view`-role users is inconsistent with the deliberate `RequiresEditRole` gating placed on `Create`/`Destroy`, and leaks operational/credential metadata that the role model intends to restrict to `edit`/`admin` users.

### Impact Explanation
A user granted only the `view` role (the lowest privilege tier, intended for read-only monitoring) can enumerate all configured external initiators and obtain their `AccessKey` and `OutgoingToken` values — data the authorization model treats as privileged, since mutating this same resource requires `edit` role. This is a role-bypass / information-disclosure issue on a credential-bearing resource, directly analogous to the reported missing-`onlyOwner` bug: an operation that manipulates/exposes sensitive access-control data is left unguarded while its sibling operations are properly guarded.

### Likelihood Explanation
High likelihood of triggering: no special conditions are required beyond having any valid, low-privilege authenticated session or API token (which is often provisioned to read-only integrators/monitoring users). The endpoint is a standard `GET` with pagination and requires no additional bypass technique.

### Recommendation
Wrap the `GET /v2/external_initiators` route with the same `auth.RequiresEditRole` (or `auth.RequiresAdminRole`) middleware used for `Create` and `Destroy`, consistent with how the analogous smart-contract fix was to add `onlyOwner` to `recoverERC20`:

```go
authv2.GET("/external_initiators", auth.RequiresEditRole(paginatedRequest(eia.Index)))
```

Additionally consider excluding `AccessKey`/`OutgoingToken` from list responses entirely, only exposing them at creation time (as already done via `ExternalInitiatorAuthentication` in `Create`).

### Proof of Concept
1. Create a user with `view` role only (`clsessions.UserRoleView`).
2. Authenticate as that user via session or API token against `AuthenticateBySession`/`AuthenticateByToken` [6](#0-5) .
3. Send `GET /v2/external_initiators` — the request passes through `authv2` group authentication only, since no role-check wraps `eia.Index` [7](#0-6) .
4. The response includes the JSON-serialized `ExternalInitiatorResource` list, containing each initiator's `accessKey` and `outgoingToken` fields [8](#0-7) , which a `view`-role user should not be entitled to obtain per the resource's `edit`-gated write operations.

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

**File:** core/web/auth/auth.go (L55-112)
```go
func AuthenticateBySession(c *gin.Context, authr Authenticator) error {
	ctx := c.Request.Context()
	session := sessions.Default(c)
	sessionID, ok := session.Get(SessionIDKey).(string)
	if !ok {
		return auth.ErrorAuthFailed
	}

	user, err := authr.AuthorizedUserWithSession(ctx, sessionID)
	if err != nil {
		return err
	}

	c.Set(SessionUserKey, &user)

	return nil
}

var _ authMethod = AuthenticateBySession

// AuthenticateByToken authenticates a User by their API token.
//
// Implements authMethod
func AuthenticateByToken(c *gin.Context, authr Authenticator) error {
	ctx := c.Request.Context()
	token := &auth.Token{
		AccessKey: c.GetHeader(APIKey),
		Secret:    c.GetHeader(APISecret),
	}
	if token.AccessKey == "" {
		return auth.ErrorAuthFailed
	}

	if token.Secret == "" {
		return auth.ErrorAuthFailed
	}

	// We need to first load the user row so we can compare tokens using the stored salt
	user, err := authr.FindUserByAPIToken(ctx, token.AccessKey)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) || errors.Is(err, clsessions.ErrUserSessionExpired) {
			return auth.ErrorAuthFailed
		}
		return err
	}

	ok, err := clsessions.AuthenticateUserByToken(token, &user)
	if err != nil {
		return err
	}
	if !ok {
		return auth.ErrorAuthFailed
	}

	c.Set(SessionUserKey, &user)

	return nil
}
```

**File:** core/web/auth/auth.go (L119-149)
```go
func AuthenticateExternalInitiator(c *gin.Context, store Authenticator) error {
	ctx := c.Request.Context()
	eia := &auth.Token{
		AccessKey: c.GetHeader(static.ExternalInitiatorAccessKeyHeader),
		Secret:    c.GetHeader(static.ExternalInitiatorSecretHeader),
	}

	ei, err := store.FindExternalInitiator(ctx, eia)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return auth.ErrorAuthFailed
		}

		return errors.Wrap(err, "finding external initiator")
	}

	ok, err := bridges.AuthenticateExternalInitiator(eia, ei)
	if err != nil {
		return err
	}
	if !ok {
		return auth.ErrorAuthFailed
	}

	// External initiator endpoints (wrapped with AuthenticateExternalInitiator) inherently assume the role
	// of 'run' (required to trigger job runs)
	c.Set(SessionExternalInitiatorKey, ei)
	c.Set(SessionUserKey, &clsessions.User{Role: clsessions.UserRoleRun})

	return nil
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
