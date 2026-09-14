### Title
Broad Role Disclosure of External Initiator Outgoing Webhook Credentials to Low-Privilege "view" Users - ([File: core/web/external_initiators_controller.go])

### Summary
The `GET /v2/external_initiators` endpoint is reachable by any authenticated user with the lowest role (`view`), and returns the `OutgoingToken` credential for every external initiator configured on the node, mirroring the CVE-2017-7486 pattern where a low-privilege grant (`USAGE`) was sufficient to read a secret credential (`pg_user_mappings` password) that should have required a higher privilege level.

### Finding Description
The route is registered without any role restriction beyond generic authentication: [1](#0-0) 

Compare this to the RBAC test matrix, which explicitly documents that this route is `viewOnlyAllowed: true`: [2](#0-1) 

The handler serializes every stored `ExternalInitiator` row (no ownership scoping — external initiators are node-wide, not per user) into a resource that includes `OutgoingToken`: [3](#0-2) [4](#0-3) 

`OutgoingToken` is generated together with `OutgoingSecret` as a credential pair at creation time (`utils.NewSecret(...)` twice), analogous to the `AccessKey`/`Secret` pairing used for *inbound* authentication: [5](#0-4) 

Only the `edit` role (and above) is required to *create* or *destroy* an external initiator: [1](#0-0) 

but *reading* the resulting `OutgoingToken` requires no more than `view`. This is an inconsistent privilege boundary: the ability to view sensitive credential material is granted to a role strictly weaker than the role required to manage the credential's lifecycle — the same structural flaw as CVE-2017-7486, where `pg_user_mappings` disclosed a secret (foreign-server password) to any principal with a weaker privilege (`USAGE`) than the one needed to create the mapping.

I was unable to locate, within the indexed portion of the codebase, the outbound notification code path that actually consumes `OutgoingToken`/`OutgoingSecret` when the node calls back an external initiator's URL (searches for `OutgoingToken`/`OutgoingSecret` usage under `core/services/webhook/**` returned no matches). This limits full confirmation of exactly how/where this token is used as a bearer credential at runtime; it is possible the full webhook-notification implementation lives in a file that exceeds the index's coverage limits.

### Impact Explanation
A logged-in user restricted to the `view` role — who should not be able to modify or manage bridges, keys, jobs, transfers, etc. — can retrieve the `OutgoingToken` for every external initiator configured on the node via a single unauthenticated-for-role GET request. If `OutgoingToken` is used as a bearer/authentication credential when the node calls back to the initiator's registered `URL`, a `view`-role account (which may be handed out broadly, e.g., to auditors, dashboards, or read-only integrations) obtains a credential it has no legitimate need for and no ability to rotate, enabling potential impersonation of the chainlink node toward the external initiator's endpoint.

### Likelihood Explanation
High reachability: this is a plain authenticated GET endpoint reachable by the weakest role in the system, requiring only valid session/API-token credentials at the `view` level — no additional privilege escalation, timing, or race condition needed. The RBAC test suite in the repo explicitly asserts and locks in this behavior (`viewOnlyAllowed: true`), meaning it is intentional current behavior rather than a subtle bug, but it is inconsistent with the write-side RBAC (`edit` required to create/destroy).

### Recommendation
Restrict `GET /v2/external_initiators` (and `Show`, if a per-item endpoint exists) to at least the `edit` role, matching the role required for `Create`/`Destroy`, or strip `OutgoingToken`/other secret-adjacent fields from the `view`-role response and only return them to `edit`/`admin` roles. Alternatively, split "read metadata" (`Name`, `URL`, timestamps) from "read credentials" (`OutgoingToken`) into a permission-scoped separate resource/endpoint, so that the credential portion is never returned unless the caller holds the `edit` role required to have created it in the first place.

### Proof of Concept
1. Create an admin/edit user and, via `POST /v2/external_initiators`, register an external initiator with a URL — this generates and stores an `OutgoingToken`.
2. Create a second user with role `view` (e.g., via `admin users create --role view` per `core/cmd/admin_commands.go`).
3. Authenticate as the `view` user and issue `GET /v2/external_initiators`.
4. Observe that the response body includes `outgoingToken` for the external initiator created in step 1, confirmed by the existing test assertions that this field is populated and returned on this route: [6](#0-5) 

The `view`-role user, who cannot create, modify, or delete any bridge/EI resource, is nonetheless able to read the outgoing credential belonging to it.

### Citations

**File:** core/web/router.go (L263-266)
```go
		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
```

**File:** core/web/auth/auth_test.go (L224-226)
```go
	{"GET", "/v2/external_initiators", true, true, true},
	{"POST", "/v2/external_initiators", false, false, true},
	{"DELETE", "/v2/external_initiators/MOCK", false, false, true},
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

**File:** core/bridges/external_initiator.go (L36-57)
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
