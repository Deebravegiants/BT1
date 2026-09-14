### Title
Sensitive `OutgoingToken` credential for External Initiators is disclosed to any authenticated user via unrestricted `GET /v2/external_initiators` endpoint - (File: core/web/router.go)

### Summary
The Jenkins CloudTest advisory describes credentials being persisted and made readable in plaintext to any party with access to the storage location, without any additional authorization gate. The Chainlink analog is `core/web/router.go`'s `GET /v2/external_initiators` route, which returns each External Initiator's plaintext `OutgoingToken` (a live authentication secret) to any authenticated user, without a role check, unlike the sibling `POST`/`DELETE` routes on the same resource.

### Finding Description
External Initiators are records that let a remote actor trigger job runs; Chainlink also uses the `OutgoingToken`/`OutgoingSecret` pair to authenticate itself back to that external initiator when it calls out (analogous to a credential used for outbound requests). These are generated and stored in plaintext (not hashed) in the `external_initiators` table: [1](#0-0) 

The incoming credential (`Secret`/`HashedSecret`) is properly hashed and salted for verification, but `OutgoingToken`/`OutgoingSecret` are necessarily stored and returned in plaintext because Chainlink must present them on outbound calls: [2](#0-1) 

The `ExternalInitiatorResource` presenter, used for the listing endpoint, includes `OutgoingToken` in its JSON output: [3](#0-2) 

Critically, the `Index` route that serves this presenter has no role restriction, while the `Create` and `Destroy` routes on the very same resource explicitly require the `Edit` role: [4](#0-3) 

This means any authenticated user — including one with only the `Read` role (the lowest-privilege authenticated role in Chainlink’s RBAC) — can call `GET /v2/external_initiators` and retrieve every configured external initiator’s `OutgoingToken` in plaintext.

### Impact Explanation
An unprivileged (`Read`-role) authenticated user can retrieve outgoing authentication tokens for all External Initiators configured on the node. If an attacker with only read access obtains these tokens, they can potentially impersonate the Chainlink node when communicating with the external initiator’s endpoint (request/response confusion, unauthorized triggering, or spoofing outbound authenticated calls), which is a credential/secret disclosure that crosses a role boundary that the codebase otherwise explicitly enforces (`RequiresEditRole` on sibling mutating routes for the same resource).

### Likelihood Explanation
Likelihood is high for any environment where the `Read` role is granted to a broader set of users (a common practice for lower-trust API consumers or dashboards), since exploitation only requires a single authenticated GET request with no additional privilege — no exotic conditions or race conditions are needed.

### Recommendation
Restrict `GET /v2/external_initiators` (and the underlying `Index` handler) to at least the `Edit` role (consistent with `Create`/`Destroy` on the same resource), or strip `OutgoingToken`/`OutgoingSecret` from the list presenter and only return them once at creation time (as is already done for the `Create` response via `ExternalInitiatorAuthentication`).

### Proof of Concept
1. Configure the node with `WebServer.AuthenticationMethod = "local"` (or any method) and create a user with `Read` role.
2. As an admin, create an External Initiator: `POST /v2/external_initiators` (requires Edit role) — note the returned `OutgoingToken`.
3. Authenticate as the `Read`-role user and call `GET /v2/external_initiators`.
4. Observe that the response JSON includes `outgoingToken` for the initiator created in step 2, confirming that a lower-privileged role than the one required to create/delete the resource can read its live outbound authentication secret.
Route reference: [4](#0-3)  ; Presenter reference: [3](#0-2)

### Citations

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

**File:** core/web/router.go (L263-266)
```go
		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
```
