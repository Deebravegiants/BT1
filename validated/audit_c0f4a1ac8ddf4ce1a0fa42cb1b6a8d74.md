Audit Report

## Title
Bridge `outgoingToken` (external adapter credential) is stored in cleartext and disclosed to any authenticated low-privilege ("view" role) user via REST and GraphQL - ([File: core/bridges/bridge_type.go])

## Summary
The `BridgeType.OutgoingToken` — the credential Chainlink uses to authenticate to an external adapter — is generated and persisted in plaintext with no encryption or hashing, unlike `IncomingToken` which is hashed before storage. Both the REST `GET /v2/bridge_types` / `GET /v2/bridge_types/:BridgeName` endpoints and the GraphQL `bridges`/`bridge` queries expose this plaintext token to any authenticated session, including the lowest-privilege "view" role, because none of these read paths apply a role check beyond basic authentication.

## Finding Description
`NewBridgeType` hashes `IncomingToken` via `incomingTokenHash` but stores `OutgoingToken` as-is in the `BridgeType` struct persisted to the `outgoing_token` column: [1](#0-0) . The `CreateBridgeType` insert writes `outgoing_token` directly with no encryption: [2](#0-1) , matching the plaintext column definition in the initial migration: [3](#0-2) .

On the REST side, `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` are registered only behind `Authenticate`, with no `RequiresEditRole`/`RequiresAdminRole` wrapper, unlike the mutating routes (`POST`/`PATCH`/`DELETE`) which explicitly require edit role: [4](#0-3) . This is confirmed by the router-rule test table which marks both GET routes as `viewOnlyAllowed: true`: [5](#0-4) . The `RequiresEditRole`/`RequiresRunRole`/`RequiresAdminRole` helpers in `core/web/auth/auth.go` demonstrate the codebase's own mechanism for restricting endpoints by role — a mechanism that was simply not applied to the bridge GET routes: [6](#0-5) . The presenter then serializes `OutgoingToken` unconditionally into the JSON response: [7](#0-6) .

On the GraphQL side, `Bridges`/`Bridge` resolvers call only `authenticateUser`, which merely confirms a valid session exists and explicitly documents that "presence of user inherently provides 'view' access" — it performs no role elevation check: [8](#0-7) , [9](#0-8) . The `Bridge` GraphQL type declares `outgoingToken: String!` and `BridgeResolver.OutgoingToken()` returns the raw stored value: [10](#0-9) , [11](#0-10) .

An analogous gap exists for `ExternalInitiator.OutgoingSecret`/`OutgoingToken`, also stored and returned in plaintext: [12](#0-11) , [13](#0-12) .

## Impact Explanation
`OutgoingToken` is a live credential used by the node to authenticate to external bridge adapters. Exposing it to "view"-role sessions — the role explicitly intended for read-only access — lets a low-privileged, authenticated user obtain a secret that should require at minimum edit/admin privileges, enabling impersonation of the node to the external adapter or reuse of the credential outside its intended scope. This is a genuine, code-level role-boundary violation (secret exfiltration via broken access control) within the node's own authenticated API, not a network- or host-level issue, and not reliant on any leaked/misconfigured credential — the gap is structural (missing role wrapper) and directly caused by the reviewed code.

## Likelihood Explanation
Exploitation requires only an authenticated session with the lowest privilege tier ("view"), which is a normal, documented, low-trust role for read-only dashboard use. No further exploitation steps, timing, or race conditions are needed — a single `GET /v2/bridge_types` request or GraphQL `bridges { outgoingToken }` query, both explicitly permitted for view-role sessions per the project's own auth test matrix, is sufficient and fully repeatable.

## Recommendation
- Redact/omit `OutgoingToken` (and `ExternalInitiator.OutgoingSecret`/`OutgoingToken`) from responses served to "view"/"run" role sessions in `BridgeResource`, `ExternalInitiatorResource`, and `BridgeResolver`/GraphQL schema; only "admin"/"edit" roles (or only bridge creation responses) should see it, mirroring how `IncomingToken` is only ever exposed on creation.
- Wrap `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` with an appropriate role check (or split response fields) and add an equivalent role check inside the `Bridges`/`Bridge` GraphQL resolvers instead of relying solely on `authenticateUser`.
- Consider encrypting `outgoing_token` (and `external_initiators` outgoing secret/token) at rest and decrypting only at the point Chainlink performs the outbound bridge call.

## Proof of Concept
1. As an admin, create a Chainlink node user/API token with `--role=view`.
2. Authenticate as that view-role user and send `GET /v2/bridge_types` (permitted per `core/web/auth/auth_test.go` route table) or execute the GraphQL query:
   ```graphql
   query { bridges(limit: 100) { results { name outgoingToken } } }
   ```
3. Observe the JSON/GraphQL response includes each bridge's `outgoingToken` in plaintext, confirming a view-role account can retrieve a credential intended to be restricted to higher-privileged roles.

### Citations

**File:** core/bridges/bridge_type.go (L71-101)
```go
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

**File:** core/bridges/orm.go (L125-140)
```go
// CreateBridgeType saves the bridge type.
func (o *orm) CreateBridgeType(ctx context.Context, bt *BridgeType) error {
	stmt := `INSERT INTO bridge_types (name, url, confirmations, incoming_token_hash, salt, outgoing_token, minimum_contract_payment, use_connection_manager, created_at, updated_at)
	VALUES (:name, :url, :confirmations, :incoming_token_hash, :salt, :outgoing_token, :minimum_contract_payment, :use_connection_manager, now(), now())
	RETURNING *;`
	err := o.transact(ctx, false, func(tx *orm) error {
		stmt, err := tx.ds.PrepareNamedContext(ctx, stmt)
		if err != nil {
			return err
		}
		defer stmt.Close()
		return stmt.GetContext(ctx, bt, bt)
	})

	return pkgerrors.Wrap(err, "CreateBridgeType failed")
}
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

**File:** core/web/router.go (L268-273)
```go
		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
```

**File:** core/web/auth/auth_test.go (L227-231)
```go
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
	{"DELETE", "/v2/bridge_types/MOCK", false, false, true},
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

**File:** core/web/resolver/query.go (L50-68)
```go
// Bridges retrieves a paginated list of bridges.
func (r *Resolver) Bridges(ctx context.Context, args struct {
	Offset *int32
	Limit  *int32
}) (*BridgesPayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}

	offset := pageOffset(args.Offset)
	limit := pageLimit(args.Limit)

	brdgs, count, err := r.App.BridgeORM().BridgeTypes(ctx, offset, limit)
	if err != nil {
		return nil, err
	}

	return NewBridgesPayload(brdgs, safeInt32(count)), nil
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

**File:** core/web/resolver/bridge.go (L52-55)
```go
// OutgoingToken resolves the bridge's outgoing token.
func (r *BridgeResolver) OutgoingToken() string {
	return r.bridge.OutgoingToken
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
