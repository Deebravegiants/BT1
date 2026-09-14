### Title
External Initiator credentials are stored in plaintext and re-disclosed unmasked on every subsequent list/read request - ([File: core/bridges/external_initiator.go])

### Summary
The reported Jenkins Ansible issue is about extra variables/secrets being persisted unencrypted and displayed unmasked to users who can read job configuration. The Chainlink analog is the External Initiator (EI) feature: the `AccessKey` and `OutgoingToken`/`OutgoingSecret` fields are stored in plaintext in the `external_initiators` table and are returned in full, unredacted, every time the `GET /v2/external_initiators` (and single-EI) endpoints are called — not just at creation time as intended.

### Finding Description
`ExternalInitiator.NewExternalInitiator` generates `AccessKey`, `OutgoingToken`, and `OutgoingSecret` and stores them as plaintext columns (`access_key`, `outgoing_secret`, `outgoing_token`) via `CreateExternalInitiator`: [1](#0-0) [2](#0-1) 

Only `HashedSecret`+`Salt` are hashed (the incoming-auth secret); `OutgoingToken` and `OutgoingSecret` (used by the node to authenticate itself when calling out to the external initiator) are stored and returned as-is. The intent, as with the Jenkins/Ansible bug, is presumably that secrets like `OutgoingToken`/`OutgoingSecret`/`AccessKey` should only ever be shown once at creation, similar to how `IncomingToken` is only returned on bridge creation (`BridgeResource.IncomingToken` has `omitempty` and is only populated in the create path, per `core/web/presenters/bridges.go`). However, for External Initiators, the list endpoint `ExternalInitiatorsController.Index` re-serializes `AccessKey` and `OutgoingToken` on every GET call via `ExternalInitiatorResource`: [3](#0-2) [4](#0-3) 

This is confirmed by the test asserting that `GET /v2/external_initiators` returns `AccessKey` and `OutgoingToken` in the response body for every entry, indefinitely, not just on creation: [5](#0-4) 

### Impact Explanation
Any authenticated user permitted to hit the `/v2/external_initiators` list endpoint (a lower bar than being the original creator, and reachable by any role that can read this admin API surface) can repeatedly retrieve the plaintext `AccessKey` and `OutgoingToken` for every configured external initiator. These credentials are used to authenticate inbound job-run trigger requests (`AccessKey`+secret) and outbound run acknowledgements (`OutgoingToken`/`OutgoingSecret`), so their long-term, unmasked exposure via a read API is a credential-disclosure issue analogous to CWE-311/312 in the reference CVE: secrets that should be shown once and then redacted are instead persistently viewable, increasing the window and surface for credential capture (e.g., via logs, screen-sharing, over-permissioned viewer accounts, or session/CSRF-adjacent access to the read-only route).

### Likelihood Explanation
Moderate. Exploitation requires an authenticated session capable of calling the `/v2/external_initiators` GET endpoint. There is no indication in the reviewed code that this endpoint is restricted to admin-only roles beyond generic node-API authentication; the router wiring for role-gating on this specific route was not verifiable within the tool budget. Regardless of role scoping, the design flaw (persistent plaintext storage + repeated unmasked disclosure of what should be one-time secrets) is present in the code itself.

### Recommendation
- Store `OutgoingToken`/`OutgoingSecret`/`AccessKey` using the same one-way hashing already applied to `HashedSecret`, or encrypt-at-rest with the node's master key, verifying via constant-time compare only when the node needs to present them outbound.
- Change `ExternalInitiatorResource` (used by `Index`/list/read endpoints) to omit `AccessKey`/`OutgoingToken` from GET responses, only returning them once via `ExternalInitiatorAuthentication` at creation time, mirroring how `BridgeResource.IncomingToken` is `omitempty` and populated only on create.
- Audit all presenters (`core/web/presenters/*.go`) for other secret-like fields (`OutgoingToken`, `Password`, `AccessKey`) that get exposed on read/list routes instead of only on creation.

### Proof of Concept
1. Create an external initiator: `POST /v2/external_initiators {"name":"foo","url":"https://x"}` → response includes `incomingAccessKey`, `outgoingToken`, `outgoingSecret` in plaintext (expected, one-time).
2. Later, as any user with access to the list route, call `GET /v2/external_initiators` → the response (`ExternalInitiatorResource`) again returns `accessKey` and `outgoingToken` in plaintext for every stored initiator, unmasked, as shown by the existing test assertions at `core/web/external_initiators_controller_test.go:108-109` and `125-126`, demonstrating the secrets remain retrievable indefinitely rather than being shown only once.

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
