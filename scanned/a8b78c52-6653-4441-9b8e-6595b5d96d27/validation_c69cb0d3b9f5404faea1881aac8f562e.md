### Title
Chainlink bridge and external-initiator API responses expose plaintext `outgoingToken`/`outgoingSecret` credentials to any authenticated Viewer/Run-role user, unmasked - ([File: core/web/presenters/bridges.go])

### Summary
`GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, and `GET /v2/external_initiators` return the bridge's `outgoingToken` (and the external initiator's `outgoingToken`/access key) in cleartext to every authenticated node user, without any role restriction or masking, mirroring the Jenkins LoadNinja Plugin issue where an API key was displayed unmasked to anyone who could view the job configuration form.

### Finding Description
`BridgeResource`, returned by both the `Index` and `Show` bridge_types endpoints and by the GraphQL `Bridge` type, always includes the plaintext `OutgoingToken` field with no `omitempty`/masking logic: [1](#0-0) 

`NewBridgeResource` copies the stored `OutgoingToken` directly from the DB-backed `bridges.BridgeType` into the response with no redaction: [2](#0-1) 

The `Index` and `Show` handlers on `BridgeTypesController` are reachable by any authenticated user, since the router only guards Create/Update/Destroy with `RequiresEditRole`, leaving `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` open to any authenticated role (including read-only "View"): [3](#0-2) 

The same pattern exists for the GraphQL `Bridge` type, which exposes `outgoingToken` with no access control differentiation from other read-only fields: [4](#0-3) [5](#0-4) 

External initiators are similar: `ExternalInitiatorResource`, returned by the unguarded `GET /v2/external_initiators` route, carries both the `AccessKey` and `OutgoingToken` unmasked: [6](#0-5) [7](#0-6) 

By contrast, the codebase demonstrates elsewhere (secrets TOML dumps) that it is aware secrets should be redacted (`xxxxx` placeholders in config output), showing the omission here is an inconsistency rather than intended behavior: [8](#0-7) 

This maps directly to the CWE-312 "Cleartext Storage/Display of Sensitive Information" class from the Jenkins advisory: a credential meant to authenticate outbound requests from the bridge/EA is displayed unmasked on a form/response any node operator user (even one with only read/run privileges) can retrieve.

### Impact Explanation
`OutgoingToken` (and, for external initiators, `AccessKey`) is the shared secret Chainlink uses to authenticate its own outgoing webhook/EA calls. Any authenticated user who can list bridges/external initiators — a low-privilege capability not gated behind `RequiresEditRole`/`RequiresAdminRole` — can read this secret and use it to impersonate the node when calling the external adapter or webhook endpoint, or to replay/spoof requests toward systems that trust that token. This is a genuine secret-disclosure issue (CWE-312 analog) reachable from a low-privileged, unprivileged-relative-to-secret-owner API client.

### Likelihood Explanation
High. No special conditions are needed — a valid session/API token with any role (View is sufficient for `GET`) can call `GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, or `GET /v2/external_initiators`, or issue the equivalent GraphQL `bridges`/`bridge` query, and the response will always contain the plaintext token.

### Recommendation
- Do not include `OutgoingToken`/`OutgoingSecret`/`AccessKey` in list/show responses returned to users without Edit/Admin role; mask them (e.g., show only a suffix or a boolean "is set") the same way `IncomingToken` is already only returned once at creation time.
- Gate `GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, and `GET /v2/external_initiators` (and their GraphQL equivalents) with `auth.RequiresEditRole` or add field-level redaction based on caller role.
- Apply the same masking to the GraphQL `Bridge.outgoingToken` resolver.

### Proof of Concept
1. Create a Viewer-role (read-only) API token/session on a running Chainlink node.
2. Create a bridge via an Edit/Admin account: `POST /v2/bridge_types {"name":"test","url":"https://ea.example.com"}`.
3. As the Viewer-role user, call `GET /v2/bridge_types/test`.
4. Observe the JSON response includes `"outgoingToken":"<plaintext secret>"`, fully readable despite the caller having no Edit privileges — confirmed by `NewBridgeResource` in `core/web/presenters/bridges.go` unconditionally populating `OutgoingToken`, and the route table in `core/web/router.go` only requiring authentication (not `RequiresEditRole`) for `GET /v2/bridge_types/:BridgeName`.

### Citations

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

**File:** core/web/presenters/bridges.go (L29-42)
```go
// NewBridgeResource constructs a new BridgeResource
func NewBridgeResource(b bridges.BridgeType) *BridgeResource {
	return &BridgeResource{
		// Uses the name as the id...Should change this to the id
		JAID:                   NewJAID(b.Name.String()),
		Name:                   b.Name.String(),
		URL:                    b.URL.String(),
		Confirmations:          b.Confirmations,
		OutgoingToken:          b.OutgoingToken,
		MinimumContractPayment: b.MinimumContractPayment,
		UseConnectionManager:   b.UseConnectionManager,
		CreatedAt:              b.CreatedAt,
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

**File:** core/web/router.go (L268-273)
```go
		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
```

**File:** core/web/resolver/bridge.go (L52-55)
```go
// OutgoingToken resolves the bridge's outgoing token.
func (r *BridgeResolver) OutgoingToken() string {
	return r.bridge.OutgoingToken
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

**File:** core/services/chainlink/testdata/secrets-full-redacted.toml (L65-72)
```text
[P2PKey]
JSON = 'xxxxx'
Password = 'xxxxx'

[CRE]
[CRE.Streams]
APIKey = 'xxxxx'
APISecret = 'xxxxx'
```
