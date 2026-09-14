### Title
External Initiator `OutgoingSecret`/`OutgoingToken` stored and retrievable in plaintext - ([File: core/bridges/external_initiator.go])

### Summary
Chainlink's External Initiator feature stores an `OutgoingSecret` and `OutgoingToken` in plaintext in the `external_initiators` table and re-exposes `OutgoingToken` on every subsequent list/read of external initiators via the API, unlike the initiator's *incoming* authentication secret, which is hashed and salted before storage.

### Finding Description
When an External Initiator (EI) is created, Chainlink generates two independent credential pairs:
- an **incoming** pair (`AccessKey`/`Secret`), used by the EI to authenticate to the node — this one is properly salted and hashed via `auth.HashedSecret` before persistence [1](#0-0) 
- an **outgoing** pair (`OutgoingToken`/`OutgoingSecret`), used by the node to authenticate itself to the EI when forwarding job-run triggers — these are stored as raw values with no hashing at all [2](#0-1) 

The database schema persists these outgoing fields as plain `text` columns with no encryption: `outgoing_secret text NOT NULL, outgoing_token text NOT NULL` [3](#0-2) .

`CreateExternalInitiator` inserts these values verbatim into the row and returns the full row (`RETURNING *`) [4](#0-3) . Critically, `OutgoingToken` (not just at creation time, but on every subsequent listing) is re-serialized into the API response resource used by `Index`: `ExternalInitiatorResource` includes `OutgoingToken` as a JSON field [5](#0-4) , and `ExternalInitiatorsController.Index` builds this resource directly from the ORM row for every EI listed [6](#0-5) .

### Impact Explanation
Any actor able to read the `external_initiators` table (via database access, backups, or DB dumps) or any node API client permitted to call the external-initiators listing endpoint recovers the outgoing token in cleartext, and (via row access) the outgoing secret. Because these values are never hashed, there is no cryptographic barrier analogous to the incoming-secret protection — a leak of the row (DB backup, replication, or a future read endpoint bug) directly discloses a live authentication credential that the node uses to call back into the external initiator, enabling request impersonation of the Chainlink node toward that initiator. This mirrors the CVE-2019-10447 analog: a credential persisted unencrypted becomes disclosable to anyone with read access to the storage layer or a permitted API surface, rather than only to the intended party.

### Likelihood Explanation
Moderate. Exploitation requires either (a) database-level read access (backup files, replicas, misconfigured DB permissions) or (b) an authenticated node-API user with sufficient role to call the external-initiators listing endpoint. The External Initiator feature itself is gated behind `ExternalInitiatorsEnabled()` and requires an authenticated role (I could not fully verify which role, e.g. Admin vs Edit, is enforced on `core/web/router.go` for this controller's routes due to indexing limits, so the exact minimum privilege for reading `OutgoingToken` back via the API is not fully confirmed).

### Recommendation
Treat `OutgoingSecret`/`OutgoingToken` the same way `Secret`/`HashedSecret` are treated for incoming auth: encrypt them at rest (e.g., using the existing keystore/AEAD utilities already used elsewhere in the codebase) or, at minimum, avoid re-exposing `OutgoingToken` in list/read responses after initial creation (return it only once, on creation, the same pattern already used for the incoming `Secret` field in `ExternalInitiatorAuthentication`). Audit `ExternalInitiatorResource` to ensure it does not leak reusable credentials on every `GET`.

### Proof of Concept
1. Create an external initiator via `POST /v2/external_initiators` (requires `ExternalInitiatorsEnabled` and appropriate node-API role): the response contains `outgoingToken`/`outgoingSecret` in plaintext, as expected on creation [7](#0-6) .
2. Later call `GET /v2/external_initiators` (Index): the returned `ExternalInitiatorResource` list again includes `outgoingToken` in plaintext for every stored initiator [5](#0-4) [6](#0-5) .
3. Alternatively, obtain a copy of the `external_initiators` table (DB dump/backup) and read `outgoing_secret`/`outgoing_token` columns directly in plaintext [3](#0-2) .

Note: I could not fully verify (due to indexing limits on `core/web/router.go`) exactly which authenticated role is required to hit the `Index` (list) route for external initiators, so the precise minimum privilege needed to retrieve `OutgoingToken` via the API remains unconfirmed; DB-level plaintext storage of both `OutgoingSecret` and `OutgoingToken`, however, is confirmed directly from the schema and ORM code cited above.

### Citations

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

**File:** core/bridges/external_initiator.go (L36-56)
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

**File:** core/bridges/orm.go (L227-243)
```go
// CreateExternalInitiator inserts a new external initiator
func (o *orm) CreateExternalInitiator(ctx context.Context, externalInitiator *ExternalInitiator) (err error) {
	query := `INSERT INTO external_initiators (name, url, access_key, salt, hashed_secret, outgoing_secret, outgoing_token, created_at, updated_at)
	VALUES (:name, :url, :access_key, :salt, :hashed_secret, :outgoing_secret, :outgoing_token, now(), now())
	RETURNING *
	`
	err = o.transact(ctx, false, func(tx *orm) error {
		var stmt *sqlx.NamedStmt
		stmt, err = tx.ds.PrepareNamedContext(ctx, query)
		if err != nil {
			return pkgerrors.Wrap(err, "failed to prepare named stmt")
		}
		defer stmt.Close()
		return pkgerrors.Wrap(stmt.GetContext(ctx, externalInitiator, externalInitiator), "failed to load external_initiator")
	})
	return pkgerrors.Wrap(err, "CreateExternalInitiator failed")
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

**File:** core/web/external_initiators_controller.go (L61-100)
```go
// Create builds and saves a new external initiator
func (eic *ExternalInitiatorsController) Create(c *gin.Context) {
	ctx := c.Request.Context()
	eir := &bridges.ExternalInitiatorRequest{}
	if !eic.App.GetConfig().JobPipeline().ExternalInitiatorsEnabled() {
		err := errors.New("The External Initiator feature is disabled by configuration")
		jsonAPIError(c, http.StatusMethodNotAllowed, err)
		return
	}

	eia := auth.NewToken()
	if err := c.ShouldBindJSON(eir); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	ei, err := bridges.NewExternalInitiator(eia, eir)
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	if err := ValidateExternalInitiator(ctx, eir, eic.App.BridgeORM()); err != nil {
		jsonAPIError(c, http.StatusBadRequest, err)
		return
	}
	if err := eic.App.BridgeORM().CreateExternalInitiator(ctx, ei); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	eic.App.GetAuditLogger().Audit(audit.ExternalInitiatorCreated, map[string]any{
		"externalInitiatorID":   ei.ID,
		"externalInitiatorName": ei.Name,
		"externalInitiatorURL":  ei.URL,
	})

	resp := presenters.NewExternalInitiatorAuthentication(*ei, *eia)
	jsonAPIResponseWithStatus(c, resp, "external initiator authentication", http.StatusCreated)
}
```
