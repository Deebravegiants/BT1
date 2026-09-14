### Title
Bridge `outgoingToken` (external adapter credential) is stored in cleartext and disclosed to any authenticated low-privilege ("view" role) user via REST and GraphQL - ([File: core/bridges/bridge_type.go])

### Summary
Chainlink's Bridge (external adapter) type stores an `OutgoingToken` credential in the `bridge_types` table without any encryption or redaction, and this credential is returned in full to any authenticated node operator API user, including the lowest-privilege "view" role, through both the REST `bridge_types` endpoints and the GraphQL `bridge`/`bridges` queries. This mirrors the referenced Jenkins Call Remote Job Plugin flaw (CVE-2019-10422): a secret needed to authenticate to a remote/external system is persisted unencrypted and exposed to users who should only have limited (read-only) visibility.

### Finding Description
`NewBridgeType` generates `IncomingToken` (hashed before storage) and `OutgoingToken` (used by Chainlink to authenticate to the external bridge adapter), but only the incoming token is hashed — the outgoing token is stored as plaintext in the `BridgeType.OutgoingToken` field/`outgoing_token` DB column: [1](#0-0) 

The `CreateBridgeType` SQL insert persists `outgoing_token` directly with no encryption: [2](#0-1) [3](#0-2) 

This plaintext token is then surfaced without additional access control:
- REST: `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` are only gated by `Authenticate` (no role check), and the route-rule test table explicitly marks these routes `viewOnlyAllowed: true`, i.e., accessible to the lowest "view" role: [4](#0-3) [5](#0-4) 
- The REST presenter includes `OutgoingToken` unconditionally in the JSON response: [6](#0-5) 
- GraphQL: the `Bridges`/`Bridge` queries only call `authenticateUser`, which merely checks for a valid session — it does not check role, so a "view" role session passes: [7](#0-6) [8](#0-7) 
- The GraphQL `Bridge` schema type exposes `outgoingToken: String!` directly, and `BridgeResolver.OutgoingToken()` returns the raw value from the DB record: [9](#0-8) [10](#0-9) 

An analogous pattern exists for `ExternalInitiator.OutgoingToken`/`OutgoingSecret`, which are also stored in plaintext and returned via the initiator presenter/controller: [11](#0-10) [12](#0-11) 

### Impact Explanation
`OutgoingToken` is the credential Chainlink uses to authenticate itself when calling out to the configured external adapter/bridge URL. Any operator-UI/API user with only "view" access — the role intended for read-only monitoring — can retrieve this secret in plaintext via the bridge listing endpoints. With this token an unprivileged (viewer-level) account can impersonate the Chainlink node to the external adapter, or reuse the credential outside its intended scope, exceeding what the "view" role is supposed to permit (CWE-522, analogous to the Jenkins Extended-Read disclosure). This is a genuine privilege/role-boundary violation within the node's own API, not a network/operator-only or mocked-only issue.

### Likelihood Explanation
Likelihood is high for any deployment that creates "view" role users (a documented, intended low-privilege role for read-only dashboards) — no additional exploitation steps are needed beyond an authenticated GET/GraphQL query that is explicitly allowed for that role per the codebase's own RBAC test matrix.

### Recommendation
- Do not return `OutgoingToken` (and `ExternalInitiator.OutgoingSecret`/`OutgoingToken`) in read/list responses for roles below "edit"/"admin"; strip or redact it in `BridgeResource`/`BridgeResolver` for view/run-role sessions, similar to how `IncomingToken` is already only exposed on creation.
- Encrypt `outgoing_token` (and analogous `external_initiators` outgoing secrets) at rest, decrypting only when Chainlink itself performs the outgoing bridge call, so the plaintext value is never persisted or served via any read API.
- Add role checks to the `bridges`/`bridge` GraphQL queries (and REST GET bridge endpoints) consistent with the intended "view" role's restricted permissions, or split the response into a public subset (name/url/confirmations) versus a privileged subset (tokens).

### Proof of Concept
1. As an admin, create a user with `--role=view` (per documented RBAC roles) or issue a "view"-role API token.
2. Authenticate as that user and call `GET /v2/bridge_types` (allowed per `auth_test.go` route table, `viewOnlyAllowed: true`) or run the GraphQL query:
```graphql
query { bridges(limit: 100) { results { name outgoingToken } } }
```
3. Observe the response contains each bridge's `outgoingToken` in plaintext — the same secret Chainlink uses to authenticate to the external adapter — despite the requesting account only having read-only "view" privileges.

### Citations

**File:** core/bridges/bridge_type.go (L55-101)
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
