Based on the investigation, I found a concrete analog: a public/sensitive route lacking the same access-control restriction (role check) that sibling routes for the same resource enforce — mirroring the source bug class of "function that should be restricted-access but is left publicly callable."

### Title
Missing role-based access control on `GET /v2/external_initiators` exposes initiator credentials to any authenticated user - (File: core/web/router.go)

### Summary
The `GET /v2/external_initiators` endpoint that lists all External Initiators is registered with no role restriction, while the `POST` and `DELETE` endpoints for the same resource explicitly require `RequiresEditRole`. This is the same class of bug as the reported issue: a function that handles sensitive data lacks the access-control modifier that its sibling functions have, allowing any authenticated caller — regardless of role — to reach it.

### Finding Description
In the `v2Routes` route table, all mutating operations on external initiators require the `edit` role: [1](#0-0) 

But the `Index` (listing) route has no `auth.RequiresEditRole`, `auth.RequiresRunRole`, or `auth.RequiresAdminRole` wrapper — only the base `authv2` group authentication (session or API token, any role) applies: [2](#0-1) [3](#0-2) 

The role hierarchy defined in `core/web/auth/auth.go` shows `view` is the lowest role and is explicitly blocked from "run" and "edit" actions, but nothing blocks `view`-role users from `Index`: [4](#0-3) [5](#0-4) 

The resource returned by this endpoint (`ExternalInitiatorResource` / `ExternalInitiatorAuthentication`) includes the initiator's `AccessKey` and `OutgoingToken` — both are credential material used to authenticate external-initiator-triggered job runs and outgoing callbacks: [6](#0-5) [7](#0-6) 

Because `Index` is unguarded by role, a lowest-privilege `view`-role user (who should only be able to read non-sensitive state) can enumerate every external initiator's `AccessKey`/`OutgoingToken`, which are effectively part of the credential pair used by `AuthenticateExternalInitiator`: [8](#0-7) [9](#0-8) 

I was unable to fully confirm from the index which presenter (`ExternalInitiatorResource` vs. the more sensitive `ExternalInitiatorAuthentication`, which also carries the raw `Secret`) is used specifically by `eia.Index` in `core/web/external_initiators_controller.go`, since the tool budget was exhausted before I could read that file's body — a Devin session with full repo access would be needed to confirm exactly which struct is serialized by `Index`.

### Impact Explanation
If `Index` serializes `AccessKey`/`OutgoingToken` (or worse, the raw secret), any authenticated `view`-role user — who is supposed to have read-only, non-privileged access — can harvest initiator credentials used to trigger job runs (`AuthenticateExternalInitiator` grants the caller `UserRoleRun` upon presenting a valid `AccessKey`/`Secret` pair) or to receive/replay outgoing callback tokens. This is a horizontal privilege escalation: a `view` user gains access to secrets that should only be reachable by `edit`/`admin` users.

### Likelihood Explanation
Likelihood is high for any deployment where multiple users with differing `UserRole` (view/run/edit/admin) share the same node, since this is a normal, supported multi-user configuration in `core/sessions`. No special conditions beyond having any valid session or API token are required — no privileged position, no malicious peer/node needed.

### Recommendation
Wrap the `GET /v2/external_initiators` route with `auth.RequiresEditRole` (or at minimum `RequiresRunRole`) to match the access level enforced on `POST`/`DELETE` for the same resource, and audit the presenter used by `Index` to ensure it does not leak `AccessKey`/`OutgoingToken`/`Secret` to any role that doesn't strictly need it.

### Proof of Concept
1. Create a user with `UserRoleView` via the admin API.
2. Authenticate as that user (session cookie or API token) against `POST /sessions`.
3. Send `GET /v2/external_initiators` with that session/token.
4. Observe the response returns the list of registered external initiators including `accessKey`/`outgoingToken` fields, despite the user only holding `view` role — compare against `POST /v2/external_initiators` and `DELETE /v2/external_initiators/:Name`, which correctly reject the same user with `401/403` due to `auth.RequiresEditRole`.

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

**File:** core/web/auth/auth.go (L116-149)
```go
// AuthenticateExternalInitiator authenticates an external initiator request.
//
// Implements authMethod
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

**File:** core/web/auth/auth.go (L198-215)
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
```

**File:** core/web/auth/auth.go (L219-234)
```go
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

**File:** core/web/presenters/external_initiators.go (L12-20)
```go
// ExternalInitiatorAuthentication includes initiator and authentication details.
type ExternalInitiatorAuthentication struct {
	Name           string        `json:"name,omitempty"`
	URL            models.WebURL `json:"url"`
	AccessKey      string        `json:"incomingAccessKey,omitempty"`
	Secret         string        `json:"incomingSecret,omitempty"`
	OutgoingToken  string        `json:"outgoingToken,omitempty"`
	OutgoingSecret string        `json:"outgoingSecret,omitempty"`
}
```

**File:** core/web/presenters/external_initiators.go (L57-65)
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
