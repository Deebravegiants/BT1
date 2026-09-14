## Analog Vulnerability Found

### Title
View-role API users can retrieve reusable outbound webhook credentials (`OutgoingToken`) for every configured External Initiator via `GET /v2/external_initiators` - ([File: core/web/external_initiators_controller.go])

### Summary
The Chainlink node's `/v2/external_initiators` list endpoint returns each External Initiator's plaintext `OutgoingToken` — a reusable secret the node uses to authenticate itself when notifying that initiator of job events — to any authenticated user holding the lowest-privilege `view` role, not just to admins/creators. This mirrors the Glances bug class: a raw object containing a reusable downstream/outbound credential is exposed via a list-style API endpoint to an actor with less privilege than the credential's sensitivity warrants.

### Finding Description
When an External Initiator is created, the node generates two distinct secret classes:
- `HashedSecret`/`Salt` — properly hashed, used to authenticate *inbound* requests from the initiator; never re-exposed after creation.
- `OutgoingToken` and `OutgoingSecret` — stored and returned as **plaintext**, generated via `utils.NewSecret(...)`, intended for the node to authenticate itself when calling *out* to the initiator's URL. [1](#0-0) 

The list endpoint `ExternalInitiatorsController.Index` fetches all initiators from the DB and maps them into `ExternalInitiatorResource`, which includes `OutgoingToken` (alongside `AccessKey`): [2](#0-1) [3](#0-2) 

This route is explicitly permitted for the `view` role — the lowest authenticated privilege tier — per the RBAC route map and its corresponding test: [4](#0-3) [5](#0-4) 

Confirmed behavior via the controller's own test, which shows `OutgoingToken` round-tripping unmodified through the list response: [6](#0-5) 

Unlike the inbound secret (`HashedSecret`), which is salted/hashed and shown only once at creation via `ExternalInitiatorAuthentication`, `OutgoingToken` is stored in plaintext and re-exposed on every subsequent list call to any authenticated caller, regardless of role, similar to how Glances re-exposed reusable pbkdf2-derived downstream credentials embedded in `uri` on every poll of `/api/4/serverslist`.

### Impact Explanation
`OutgoingToken` is intended as proof that a request purporting to originate from the Chainlink node is authentic when it calls out to the External Initiator's webhook. A `view`-role user — who under the node's role model should have read-only visibility and no ability to act as, or impersonate, the node — can retrieve this token for every configured initiator. This enables:
- Credential disclosure of a live, reusable outbound authentication secret (CWE-200/CWE-522 analog).
- Request impersonation: a low-privilege user could use the disclosed token to forge notifications appearing to originate from the Chainlink node toward each external initiator's server, if the initiator relies on that token to validate authenticity.

I was unable to locate the code path in this index that actually attaches `OutgoingToken`/`OutgoingSecret` as headers when the node notifies an External Initiator (the historical "webhook job creation notifies EIs" flow referenced in `CHANGELOG.md`); this logic may be part of legacy/deprecated JSON-spec job pipeline code not present in the indexed subset, so I cannot fully confirm the current consumption path or whether it has since been removed. This uncertainty should be verified in a full checkout before treating this as conclusively exploitable at the current severity claimed.

### Likelihood Explanation
Any user granted the `view` role (the intended minimally-trusted API role, often given to read-only dashboards/monitoring integrations) can trivially call `GET /v2/external_initiators` with valid session credentials — no special privilege escalation required. The route is unconditionally listed as `view`-permitted in the RBAC table and verified via `TestRBAC_Routemap_ViewOnly`.

### Recommendation
- Exclude `OutgoingToken` (and any other outbound authentication secret) from the `ExternalInitiatorResource` returned by `GET /v2/external_initiators`; return only non-secret metadata (`Name`, `URL`, `CreatedAt`, `UpdatedAt`) plus, if needed, a boolean indicating a token exists.
- If operational tooling truly needs to re-view `OutgoingToken`, restrict that capability to `admin`/`edit` roles rather than `view`, consistent with how `HashedSecret` is never re-exposed.
- Confirm whether `OutgoingToken`/`OutgoingSecret` are still consumed anywhere in the current webhook-notification path; if unused (dead code from the deprecated JSON job-spec pipeline), remove the fields entirely to eliminate the exposure.

### Proof of Concept
1. Create a Chainlink API user with role `view` (`chainlink admin users create --role=view`), confirmed supported via `core/cmd/admin_commands.go` and `sessions.UserRoleView`.
2. Log in as that user and call:
   ```
   GET /v2/external_initiators?size=50
   ```
3. Observe the JSON:API response contains, for every configured initiator, `accessKey` and `outgoingToken` fields — as validated by the existing test assertions in `core/web/external_initiators_controller_test.go:108-109,125-126`, which show `OutgoingToken` returned unchanged in the list payload.
4. A `view`-role holder now possesses a live outbound authentication secret for every configured External Initiator, exceeding the intended read-only trust boundary of that role.

### Citations

**File:** core/bridges/external_initiator.go (L21-56)
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

**File:** core/web/auth/auth_test.go (L224-224)
```go
	{"GET", "/v2/external_initiators", true, true, true},
```

**File:** core/web/auth/auth_test.go (L484-532)
```go
func TestRBAC_Routemap_ViewOnly(t *testing.T) {
	t.Parallel()
	app := cltest.NewApplicationEVMDisabled(t)
	require.NoError(t, app.Start(t.Context()))

	router := web.Router(t, app, nil)
	ts := httptest.NewServer(router)
	defer ts.Close()

	// Create a test run user to work with
	u := &cltest.User{Role: sessions.UserRoleView}
	client := app.NewHTTPClient(u)

	// Assert all view only routes
	for i, route := range routesRolesMap {
		t.Run(fmt.Sprintf("%d-%s-%s", i, route.verb, route.path), func(t *testing.T) {
			t.Parallel()
			var resp *http.Response
			var cleanup func()

			switch route.verb {
			case "GET":
				resp, cleanup = client.Get(route.path)
			case "POST":
				resp, cleanup = client.Post(route.path, nil)
			case "DELETE":
				resp, cleanup = client.Delete(route.path)
			case "PATCH":
				resp, cleanup = client.Patch(route.path, nil)
			case "PUT":
				resp, cleanup = client.Put(route.path, nil)
			default:
				t.Fatalf("Unknown HTTP verb %s\n", route.verb)
			}
			defer cleanup()

			// If this route only allows view only, don't expect an unauthorized response
			switch {
			case route.viewOnlyAllowed:
				assert.NotEqual(t, http.StatusUnauthorized, resp.StatusCode)
				assert.NotEqual(t, http.StatusForbidden, resp.StatusCode)
			case !route.EditAllowed:
				assert.Equal(t, http.StatusForbidden, resp.StatusCode)
			default:
				assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
			}
		})
	}
}
```

**File:** core/web/external_initiators_controller_test.go (L77-127)
```go
	eiFoo := cltest.MustInsertExternalInitiatorWithOpts(t, borm, cltest.ExternalInitiatorOpts{
		NamePrefix:    "foo",
		URL:           cltest.MustWebURL(t, "http://example.com/foo"),
		OutgoingToken: "outgoing_token",
	})
	eiBar := cltest.MustInsertExternalInitiatorWithOpts(t, borm, cltest.ExternalInitiatorOpts{NamePrefix: "bar"})

	resp, cleanup := client.Get("/v2/external_initiators?size=x")
	t.Cleanup(cleanup)
	cltest.AssertServerResponse(t, resp, http.StatusUnprocessableEntity)

	resp, cleanup = client.Get("/v2/external_initiators?size=1")
	t.Cleanup(cleanup)
	cltest.AssertServerResponse(t, resp, http.StatusOK)
	body := cltest.ParseResponseBody(t, resp)

	metaCount, err := cltest.ParseJSONAPIResponseMetaCount(body)
	require.NoError(t, err)
	require.Equal(t, 2, metaCount)

	var links jsonapi.Links
	var externalInitiators []presenters.ExternalInitiatorResource
	err = web.ParsePaginatedResponse(body, &externalInitiators, &links)
	require.NoError(t, err)
	assert.NotEmpty(t, links["next"].Href)
	assert.Empty(t, links["prev"].Href)

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
}
```
