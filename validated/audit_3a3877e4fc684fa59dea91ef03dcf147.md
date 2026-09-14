### Title
Unrestricted `GET /v2/external_initiators` leaks node-side webhook credentials (`AccessKey`, `OutgoingToken`) to any authenticated "view"-role user - ([File: core/web/router.go])

### Summary
The `GET /v2/external_initiators` endpoint requires only baseline authentication (session or API token), unlike every other create/update/delete route on the same resource and unlike sibling key-management resources, which explicitly gate mutation with `RequiresEditRole`/`RequiresAdminRole`. Any authenticated user, even one holding the lowest privilege ("view") role, can enumerate all configured External Initiators and receive their `AccessKey` and `OutgoingToken` secret fields in the response.

### Finding Description
The route registration in `v2Routes` wires the `Index` handler without any role check: [1](#0-0) 

Compare this to the neighboring `Create`/`Destroy` handlers on the very same resource, both of which are wrapped in `auth.RequiresEditRole`, and to the RBAC middleware itself, which defines four escalating roles (`view` < `run` < `edit` < `admin`): [2](#0-1) 

The `Index` handler serializes every stored `ExternalInitiator` into an `ExternalInitiatorResource`, which includes the initiator's `AccessKey` and `OutgoingToken`: [3](#0-2) [4](#0-3) 

`AccessKey`/secret pairs are the credential the node uses to authenticate inbound calls from an External Initiator (`AuthenticateExternalInitiator`), and `OutgoingToken`/`OutgoingSecret` are the credentials the node sends outbound to the initiator's callback URL so the initiator can verify the call came from the Chainlink node: [5](#0-4) [6](#0-5) 

Because the RBAC design explicitly reserves the ability to view/manage sensitive credential material (ETH/VRF/CSA keys, users, transfers) to `edit`/`admin` roles, exposing `AccessKey`/`OutgoingToken` to `view`-role sessions is an inconsistency in the privilege model — the "unprivileged" role in Chainlink's own RBAC (`view`) is granted a level of secret disclosure that the system's design elsewhere treats as requiring elevated roles.

### Impact Explanation
`AccessKey` is one half of the credential pair needed to authenticate as the External Initiator when calling the node's job-run-triggering endpoints (`AuthenticateExternalInitiator` flow), and `OutgoingToken` is part of the credential set that downstream integrations trust to validate that a request truly originated from the Chainlink node. Disclosure of these values to any authenticated low-privilege user (e.g., a `view`-role account meant only for dashboards/monitoring) undermines the authentication boundary between roles and could facilitate impersonation of the External Initiator relationship or unauthorized triggering of job runs, depending on how the initiator's own callback validates `OutgoingToken`.

### Likelihood Explanation
Likelihood is Low/Medium: it requires an attacker to already hold a valid, authenticated Chainlink node account with the lowest role (`view`), which is a normal, low-trust tier of access commonly handed out for read-only dashboard use. No further privilege escalation or exploit is needed beyond calling `GET /v2/external_initiators`.

### Recommendation
Wrap the `Index` route with `auth.RequiresEditRole` (matching `Create`/`Destroy` on the same resource), or strip `AccessKey`/`OutgoingToken` from `ExternalInitiatorResource` for list/show responses, only returning full credentials once, at creation time (as already done via `ExternalInitiatorAuthentication` in `Create`).

### Proof of Concept
1. Create a local user with role `view` (the minimum RBAC role) via the admin CLI/API.
2. Authenticate as that user (`AuthenticateBySession` or `AuthenticateByToken`).
3. Call `GET /v2/external_initiators`.
4. Because the route in [7](#0-6)  has no `auth.RequiresXRole` wrapper (unlike `POST`/`DELETE` on the same path), the request succeeds and the JSON response contains each registered initiator's `accessKey` and `outgoingToken` fields as defined in [8](#0-7) , disclosing secret material to a role that should not be able to view or manage External Initiator credentials.

### Citations

**File:** core/web/router.go (L263-266)
```go
		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
```

**File:** core/web/auth/auth.go (L217-253)
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

// RequiresAdminRole extracts the user object from the context, and asserts the user's role is 'admin'
func RequiresAdminRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role != clsessions.UserRoleAdmin {
			c.Abort()
			addForbiddenErrorHeaders(c, "admin", string(user.Role), user.Email)
			jsonAPIError(c, http.StatusForbidden, errors.New("Forbidden"))
			return
		}
		handler(c)
	}
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
