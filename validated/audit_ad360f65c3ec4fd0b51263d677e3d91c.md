### Title
Bridge outgoing tokens stored and transmitted in cleartext, allowing indefinite disclosure of external-adapter shared secrets - (File: `core/bridges/bridge_type.go`, `core/store/migrate/migrations/0001_initial.sql`, `core/web/presenters/bridges.go`)

### Summary
The GHSA-9p5v-6p5f-f28h advisory describes the Jenkins Mashup Portlets plugin storing credentials unencrypted on disk, where anyone with read access could recover the plaintext secret. Chainlink has an analogous pattern in its Bridge (external adapter) credential model: the `outgoing_token` used to authenticate Chainlink's outbound requests to an external adapter is generated once and then persisted and served back in plaintext forever, with no hashing/rotation, unlike the paired `incoming_token`, which is hashed with a per-record salt.

### Finding Description
`bridges.NewBridgeType` in <cite repo="Alyssadaypin/chainlink--019" path="core/bridges/bridge_type.go" start="70,101" /> generates two secrets: `incomingToken` (hashed via `incomingTokenHash` before being stored as `IncomingTokenHash`/`Salt`) and `outgoingToken`, which is stored as plaintext in the `BridgeType.OutgoingToken` field: [1](#0-0) 

The database schema persists this value in cleartext with no encryption column type distinguishing it from other data: [2](#0-1) 

`ORM.CreateBridgeType`/`BridgeTypes` read/write this column directly via `SELECT *` and parameterized inserts with no decryption/encryption step: [3](#0-2) 

Unlike the salted-hash design used for `IncomingTokenHash`, the `OutgoingToken` is never hashed, so it can be recovered in plaintext by:
- Any code path with DB read access (dump/backup/log of `bridge_types` table).
- Any authenticated node API/GraphQL user who can query bridges — the REST/GraphQL presenters explicitly re-expose the value: [4](#0-3) 

The `OutgoingToken` is likewise returned unmodified from `ExternalInitiatorAuthentication`/`BridgeTypeAuthentication` presenter structures on creation/query, meaning the token is transmitted and stored plaintext end-to-end, contrasting with password/secret redaction elsewhere in the codebase (e.g., `isBlacklisted` password field redaction in HTTP logging, `config.SecretString` "xxxxx" masking used for `Password`/`AuthToken` TOML config fields): [5](#0-4) [6](#0-5) 

### Impact Explanation
The `OutgoingToken` is a bearer credential Chainlink uses to authenticate to the external adapter (the adapter validates the `Authorization` header against this value). If disclosed — via DB backup access, log capture, or a bridges list/read query available to any authenticated node-API user (`Bridges` GraphQL query / `/v2/bridge_types` REST endpoint are readable by non-admin roles in most configurations) — an attacker can impersonate the Chainlink node when calling the adapter, or replay/forge requests that the adapter trusts as coming from the legitimate node. This is a direct analog of CWE-522 (insufficiently protected credentials): the secret is persisted unencrypted and can be viewed by anyone with read access to the store, exactly like the Jenkins plugin flaw.

### Likelihood Explanation
Likelihood is moderate: exploitation requires either (a) database/backup read access, or (b) an authenticated node-API/GraphQL session capable of listing bridges. The bridge list/read endpoints are accessible to non-admin authenticated roles in the node's web API in many configurations, and the value is deliberately re-serialized in full on every bridge read (not just at creation), unlike `IncomingTokenHash`, increasing the exposure window significantly relative to a one-time reveal.

### Recommendation
- Store `OutgoingToken` using the same encryption/redaction pattern already used elsewhere in the codebase (`config.SecretString`/`SecretURL`) or symmetric encryption at rest, decrypting only when establishing the outbound call to the external adapter.
- Stop returning `OutgoingToken` in full on subsequent bridge reads (`FindBridge`/`BridgeTypes`/GraphQL resolvers) — only reveal it once at creation/rotation time, mirroring the one-time reveal behavior of `IncomingToken`.
- Add `OutgoingToken`/`outgoingToken` to the HTTP/GraphQL response redaction and audit-log blacklists, consistent with `core/web/router.go`'s existing `isBlacklisted` password redaction.
- Support rotation of the outgoing token independent of bridge recreation.

### Proof of Concept
1. Create a bridge via `POST /v2/bridge_types` as any user with bridge-create/read permission; response includes plaintext `outgoingToken` (see `core/web/bridge_types_controller_test.go` assertions on `attributes.outgoingToken`).
2. Later, query the same bridge via `GET /v2/bridge_types/{name}` or the GraphQL `bridge(id: ...)` query — the plaintext `outgoingToken` is again returned in full, as shown in `core/web/resolver/bridge_test.go` (`"outgoingToken": "outgoingToken"`).
3. Alternatively, any party with read access to a database backup/dump of the `bridge_types` table (`core/store/migrate/migrations/0001_initial.sql`) can directly read the `outgoing_token` column in cleartext, exactly mirroring the Jenkins Mashup Portlets vulnerability where stored credentials were viewable by anyone with filesystem/master access.

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

**File:** core/bridges/orm.go (L108-140)
```go
// BridgeTypes returns bridge types ordered by name filtered limited by the
// passed params.
func (o *orm) BridgeTypes(ctx context.Context, offset int, limit int) (bridges []BridgeType, count int, err error) {
	err = o.transact(ctx, true, func(tx *orm) error {
		if err = tx.ds.GetContext(ctx, &count, "SELECT COUNT(*) FROM bridge_types"); err != nil {
			return pkgerrors.Wrap(err, "BridgeTypes failed to get count")
		}
		sql := `SELECT * FROM bridge_types ORDER BY name asc LIMIT $1 OFFSET $2;`
		if err = tx.ds.SelectContext(ctx, &bridges, sql, limit, offset); err != nil {
			return pkgerrors.Wrap(err, "BridgeTypes failed to load bridge_types")
		}
		return nil
	})

	return
}

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

**File:** core/web/resolver/bridge_test.go (L24-38)
```go
				bridges {
					results {
						id
						name
						url
						confirmations
						outgoingToken
						minimumContractPayment
						createdAt
					}
					metadata {
						total
					}
				}
			}`
```

**File:** core/web/router.go (L643-658)
```go
// NOTE: keys must be in lowercase for case insensitive match
var blacklist = map[string]struct{}{
	"password":             {},
	"newpassword":          {},
	"oldpassword":          {},
	"current_password":     {},
	"new_account_password": {},
}

func isBlacklisted(k string) bool {
	lk := strings.ToLower(k)
	if _, ok := blacklist[lk]; ok || strings.Contains(lk, "password") {
		return true
	}
	return false
}
```

**File:** core/store/models/secrets.go (L7-12)
```go
// Secret is a string that formats and encodes redacted, as "xxxxx".
// Deprecated
type Secret = config.SecretString

// Deprecated
func NewSecret(s string) *Secret { return config.NewSecretString(s) }
```
