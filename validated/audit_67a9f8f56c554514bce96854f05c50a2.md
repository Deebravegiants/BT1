Audit Report

## Title
Bridge `OutgoingToken` (external adapter credential) is stored and returned in plaintext to any authenticated `view`-role user - ([File: core/bridges/bridge_type.go], [File: core/web/router.go], [File: core/web/resolver/auth.go])

## Summary
Chainlink bridges have two secrets: `IncomingToken` (hashed at rest, returned only once at creation) and `OutgoingToken` (used by the node to authenticate to the external adapter), which is stored in plaintext in the `bridge_types.outgoing_token` column and returned unconditionally by both REST and GraphQL read endpoints. Critically, these read endpoints only require a valid authenticated session and do not enforce the `edit`/`admin` role that is required for bridge create/update/delete, so the lowest-privilege `view`-role user can read every bridge's plaintext `OutgoingToken`.

## Finding Description
`NewBridgeType` generates `outgoingToken := utils.NewSecret(24)` and stores it verbatim in `BridgeType.OutgoingToken`, mapped to the plain `text` column `outgoing_token`. [1](#0-0) [2](#0-1) [3](#0-2) 

`BridgeResource` unconditionally serializes `OutgoingToken` (no `omitempty`, unlike `IncomingToken` which is documented as "only provided when creating a Bridge"). [4](#0-3) 

Route-level access control in `v2Routes` confirms the read paths for bridges require no elevated role: `GET /v2/bridge_types` (`Index`) and `GET /v2/bridge_types/:BridgeName` (`Show`) are registered with no `RequiresEditRole`/`RequiresAdminRole` wrapper, while `POST`, `PATCH`, and `DELETE` on the same resource are correctly wrapped with `auth.RequiresEditRole`. [5](#0-4) 

The GraphQL layer exhibits the same gap: `authenticateUser` — used for the `bridges`/`bridge` queries — only checks that a session exists ("presence of user inherently provides 'view' access") and does not check role, whereas mutations use `authenticateUserCanEdit`/`authenticateUserIsAdmin` which do check role. [6](#0-5) [7](#0-6)  The GraphQL `Bridge` type schema also exposes `outgoingToken: String!` with no redaction. [8](#0-7) 

This confirms that a session belonging to a user with `sessions.UserRoleView` — the lowest of the four roles (`admin`, `edit`, `run`, `view`) defined in the multi-user role system — passes both the REST route middleware and the GraphQL query-level authorization check and can retrieve the plaintext `OutgoingToken` for any bridge. [9](#0-8) [10](#0-9) 

## Impact Explanation
`OutgoingToken` is a credential the node uses to authenticate itself to external adapter services. A user restricted to the `view` role — intended for read-only monitoring — can exfiltrate this credential for every configured bridge and use it to impersonate the node when calling the external adapter directly, bypassing the intended role-based segregation of duties between `view` and `edit`/`admin` users. This is a legitimate secret/credential exfiltration via a broken role-based access control boundary, distinct from generic "leaked credential" exclusions since the leak itself is caused by the application's own authorization logic returning the secret to an under-privileged principal.

## Likelihood Explanation
Exploitation requires only a valid `view`-role session (the lowest privilege tier that an admin can provision, or that can be assigned via LDAP/OIDC group mapping) and a single unmodified GET request or GraphQL query — no additional bypass, timing, or race condition is needed. This is trivially repeatable and deterministic.

## Recommendation
- Do not return `OutgoingToken` in plaintext to `view`-role sessions; require at least `edit` role for `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName`, or omit `OutgoingToken` from the response for lower-privileged roles.
- Apply the same role check to the GraphQL `bridges`/`bridge` resolvers (`authenticateUserCanEdit` or higher) or strip `outgoingToken` from the `Bridge` GraphQL type response for `view` role.
- Consider hashing `OutgoingToken` at rest (as is already done for `IncomingToken`) and only exposing it once at creation time, having internal bridge-calling code fetch/derive it through a secure internal path rather than via the general read API.

## Proof of Concept
1. As an admin, create a bridge via `POST /v2/bridge_types` and note the plaintext `outgoingToken` in the response.
2. Create a second user with `newRole=view` via `PATCH /v2/users` (admin-only) or provision via LDAP/OIDC read-group mapping.
3. Authenticate as the `view`-role user and call `GET /v2/bridge_types/:BridgeName` (or the GraphQL `bridge(name: "...")`/`bridges` query with the `outgoingToken` field selected).
4. Observe the response contains the same plaintext `outgoingToken`, despite this user having only `view` privileges and being blocked by `auth.RequiresEditRole` from creating/updating/deleting bridges — confirming the read path lacks equivalent role enforcement. This can be verified as a Go integration test against `BridgeTypesController.Show`/`Index` in `core/web/bridge_types_controller.go` and the `bridges`/`bridge` resolvers in `core/web/resolver/bridge.go`, asserting a 200/plaintext-token response for a `UserRoleView` session.

### Citations

**File:** core/bridges/bridge_type.go (L57-68)
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
```

**File:** core/bridges/bridge_type.go (L75-101)
```go
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

**File:** core/store/migrate/migrations/0001_initial.sql (L132-142)
```sql
CREATE TABLE public.bridge_types (
    name text NOT NULL,
    url text NOT NULL,
    confirmations bigint DEFAULT 0 NOT NULL,
    incoming_token_hash text NOT NULL,
    salt text NOT NULL,
    outgoing_token text NOT NULL,
    minimum_contract_payment character varying(255),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
```

**File:** core/web/presenters/bridges.go (L10-22)
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
```

**File:** core/web/router.go (L268-273)
```go
		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
```

**File:** core/web/resolver/auth.go (L11-17)
```go
// Authenticates the user from the session cookie, presence of user inherently provides 'view' access.
func authenticateUser(ctx context.Context) error {
	if _, ok := auth.GetGQLAuthenticatedSession(ctx); !ok {
		return unauthorizedError{}
	}
	return nil
}
```

**File:** core/web/resolver/auth.go (L19-55)
```go
// Authenticates the user from the session cookie and asserts at least 'run' role.
func authenticateUserCanRun(ctx context.Context) error {
	session, ok := auth.GetGQLAuthenticatedSession(ctx)
	if !ok {
		return unauthorizedError{}
	}
	if session.User.Role == sessions.UserRoleView {
		return RoleNotPermittedError{session.User.Role}
	}
	return nil
}

// Authenticates the user from the session cookie and asserts at least 'edit' role.
func authenticateUserCanEdit(ctx context.Context) error {
	session, ok := auth.GetGQLAuthenticatedSession(ctx)
	if !ok {
		return unauthorizedError{}
	}
	switch session.User.Role {
	case sessions.UserRoleView, sessions.UserRoleRun:
		return RoleNotPermittedError{session.User.Role}
	default:
	}
	return nil
}

// Authenticates the user from the session cookie and asserts has 'admin' role
func authenticateUserIsAdmin(ctx context.Context) error {
	session, ok := auth.GetGQLAuthenticatedSession(ctx)
	if !ok {
		return unauthorizedError{}
	}
	if session.User.Role != sessions.UserRoleAdmin {
		return RoleNotPermittedError{session.User.Role}
	}
	return nil
}
```

**File:** core/web/schema/type/bridge.graphql (L1-10)
```text
type Bridge {
    id: ID!
    name: String!
    url: String!
    confirmations: Int!
    outgoingToken: String!
    minimumContractPayment: String!
    useConnectionManager: Boolean!
    createdAt: Time!
}
```

**File:** core/sessions/user.go (L27-34)
```go
type UserRole string

const (
	UserRoleAdmin UserRole = "admin"
	UserRoleEdit  UserRole = "edit"
	UserRoleRun   UserRole = "run"
	UserRoleView  UserRole = "view"
)
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
