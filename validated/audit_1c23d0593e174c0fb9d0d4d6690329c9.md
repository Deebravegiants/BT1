All claims in the report are confirmed as factually accurate against the codebase. The route is registered without any role-gating middleware (only base session/token authentication), while the sibling Create/Destroy routes require `auth.RequiresEditRole`. The `Index` handler serializes results through `ExternalInitiatorResource`, which includes the plaintext `OutgoingToken` field, and the RBAC test table explicitly marks this route `viewOnlyAllowed: true`.All findings are fully verified against the codebase. Every code citation in the report matches the actual source exactly.

Audit Report

## Title
Unprivileged "View" role can read outgoing secret tokens for External Initiators via `GET /v2/external_initiators` - (File: core/web/external_initiators_controller.go)

## Summary
The `GET /v2/external_initiators` route is registered with only base session/token authentication and no elevated-role check, unlike the sibling `Create`/`Destroy` routes which require `auth.RequiresEditRole`. [1](#0-0)  The `Index` handler serializes each stored `ExternalInitiator` via `presenters.NewExternalInitiatorResource`, which includes the plaintext `OutgoingToken` field in the response. [2](#0-1) [3](#0-2) 

## Finding Description
`OutgoingToken` is generated at creation time as one of two secrets (`OutgoingToken`, `OutgoingSecret`) the node uses to authenticate its own outbound webhook calls to the initiator's configured URL. [4](#0-3)  On creation, this secret is intentionally returned once via `ExternalInitiatorAuthentication`. [5](#0-4) 

However, the list route `authv2.GET("/external_initiators", paginatedRequest(eia.Index))` has no role-gating middleware applied, in contrast to `POST`/`DELETE` on the same resource which explicitly wrap with `auth.RequiresEditRole`. [1](#0-0)  The RBAC test table explicitly documents `{"GET", "/v2/external_initiators", true, true, true}` — meaning `viewOnlyAllowed` is `true`, i.e., the lowest-privilege `UserRoleView` role can call this endpoint without error. [6](#0-5)  The `Index` handler queries all `ExternalInitiator` rows and maps each into `ExternalInitiatorResource`, which re-exposes the same `OutgoingToken` secret field that was meant to be one-time-shown on creation. [7](#0-6)  The integration test `TestExternalInitiatorsController_Index` confirms the plaintext `OutgoingToken` is present and asserted equal to the originally generated value in the list response body for every returned initiator. [8](#0-7) 

This constitutes a broken security assumption: secret material that should only be disclosed once, to the privileged actor who created it, is instead persistently readable by any authenticated user regardless of role, because the read path lacks the same authorization gate as the write paths.

## Impact Explanation
Disclosure of `OutgoingToken` to a View-role user allows that lower-privileged, non-administrative account to obtain the credential the Chainlink node uses to authenticate its outbound calls to the external initiator's remote service. This is a legitimate secret-exfiltration/credential-disclosure issue across a privilege boundary defined by the application's own RBAC model (View vs. Edit/Admin), matching the "key/secret exfiltration" and "request impersonation" impact categories.

## Likelihood Explanation
Exploitation requires only a valid View-role session/API token — a supported, intentionally low-privilege role — and a single unauthenticated-role-gated `GET` request to a paginated list endpoint. Any deployment that has provisioned View-role accounts (a normal, documented RBAC use case) and has configured at least one External Initiator is affected with no additional preconditions.

## Recommendation
Gate `GET /v2/external_initiators` behind `auth.RequiresEditRole` (matching `Create`/`Destroy`), or strip `OutgoingToken`/`OutgoingSecret` from `ExternalInitiatorResource` used by the list/Index path, disclosing those secrets only once via `ExternalInitiatorAuthentication` at creation time.

## Proof of Concept
1. As an admin, create a View-role user and obtain their session/API token.
2. As admin, `POST /v2/external_initiators {"name":"foo","url":"http://example.com"}`; capture the one-time `outgoingToken` from the response.
3. Authenticate as the View-role user and call `GET /v2/external_initiators`.
4. Observe the JSON response includes `outgoingToken` for the initiator — confirmed by the existing test `TestExternalInitiatorsController_Index`, which asserts `externalInitiators[0].OutgoingToken` equals the value generated at creation. [8](#0-7)

### Citations

**File:** core/web/router.go (L263-266)
```go
		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
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

**File:** core/web/external_initiators_controller.go (L92-99)
```go
	eic.App.GetAuditLogger().Audit(audit.ExternalInitiatorCreated, map[string]any{
		"externalInitiatorID":   ei.ID,
		"externalInitiatorName": ei.Name,
		"externalInitiatorURL":  ei.URL,
	})

	resp := presenters.NewExternalInitiatorAuthentication(*ei, *eia)
	jsonAPIResponseWithStatus(c, resp, "external initiator authentication", http.StatusCreated)
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

**File:** core/web/auth/auth_test.go (L224-224)
```go
	{"GET", "/v2/external_initiators", true, true, true},
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
