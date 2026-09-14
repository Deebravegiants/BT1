### Title
External Initiator `URL` field accepts `javascript:` URIs via `url.ParseRequestURI`, enabling stored XSS when rendered in the Operator UI - (File: `core/store/models/common.go`)

### Summary
The `WebURL` type used by Chainlink's External Initiator feature validates URLs using `url.ParseRequestURI`, which only checks that a string is a syntactically valid absolute URI or absolute path — it does not restrict the URL scheme. An authenticated user with only the "edit" role (not admin) can create an External Initiator whose `url` field is `javascript:...`, which is accepted, persisted, and later returned to admin users via the API for rendering in the Operator UI.

### Finding Description
`WebURL.UnmarshalJSON` parses the incoming `url` JSON field using `url.ParseRequestURI`: [1](#0-0) 

`url.ParseRequestURI` in Go accepts any string with a valid URI scheme (e.g. `javascript:alert(1)`) as an "absolute URI," because it does not enforce an allowlist of schemes such as `http`/`https`. This is the same root-cause bug class as CVE-2026-53472 (insufficient validation of `AgentStatusUpdate.CredentialUrl` allowing `javascript:` URLs).

This `WebURL`-typed field is exactly the `URL` field on `bridges.ExternalInitiatorRequest`, which is bound directly from the request body in the `Create` handler: [2](#0-1) 

The `ValidateExternalInitiator` function only validates the `Name` field (alphanumeric/underscore/dash and uniqueness) — it never inspects or restricts the `URL` scheme: [3](#0-2) 

The route requires only `RequiresEditRole`, not `RequiresAdminRole`: [4](#0-3) 

The stored malicious URL is then served back unmodified through the `Index` listing endpoint (`GET /v2/external_initiators`, itself unauthenticated-role-gated beyond basic session/token auth) as `presenters.ExternalInitiatorResource`, for consumption by the Operator UI: [5](#0-4) 

If the Operator UI (or any admin-facing console) renders this URL as a clickable link or otherwise injects it without re-validating the scheme, clicking it executes attacker-controlled JavaScript in the session of the viewing (higher-privileged) user — directly analogous to the Hybrid Cloud Console rendering `CredentialUrl` from `AgentStatusUpdate` in the reported CVE.

### Impact Explanation
An "edit"-role (non-admin) authenticated user can plant a `javascript:` URL that persists in the node's database indefinitely. When an admin or other operator later views the External Initiators list in the Operator UI and interacts with the malicious entry (e.g., clicking a rendered link), arbitrary JavaScript executes in that higher-privileged user's browser session — enabling session hijacking, credential theft, or privileged actions performed on the admin's behalf. This matches CVSS vector `AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:N` (low-privilege authenticated attacker, user interaction required, confidentiality impact high via session compromise).

### Likelihood Explanation
Likelihood is moderate-to-high: creating an External Initiator only requires the "edit" role (not admin), is accessible via a single documented, unauthenticated-scheme-agnostic POST request, and the payload (`javascript:...`) is a well-known XSS primitive that requires no further bypass of input validation, since none of the existing checks (`externalInitiatorNameRegexp`, duplicate-name check) inspect the URL's scheme.

### Recommendation
Restrict `WebURL` (or specifically the External Initiator `URL` field) to an explicit allowlist of schemes (`http`, `https`) at validation time, similar to the pattern already used elsewhere in the codebase, e.g. `WorkflowFetcherConfig.ValidateConfig`: [6](#0-5) 

Apply the same scheme check inside `ValidateExternalInitiator` (or `WebURL.UnmarshalJSON`/`Scan`) so that any URL with a non-http(s) scheme is rejected before being persisted, and ensure the Operator UI escapes/does not directly navigate to unsanitized stored URLs.

### Proof of Concept
1. Authenticate as a user holding only the "edit" role.
2. Send:
```
POST /v2/external_initiators
{"name":"exploit","url":"javascript:alert(document.cookie)"}
```
3. The request succeeds (`201 Created`) because `ValidateExternalInitiator` only checks `Name`, and `WebURL.UnmarshalJSON`/`url.ParseRequestURI` accepts the `javascript:` scheme.
4. `GET /v2/external_initiators` returns the stored malicious URL in the JSON response, which the Operator UI renders for admin users, resulting in stored XSS upon interaction.

### Citations

**File:** core/store/models/common.go (L118-134)
```go
func (w *WebURL) UnmarshalJSON(j []byte) error {
	var v string
	err := json.Unmarshal(j, &v)
	if err != nil {
		return err
	}
	// handle no url case
	if len(v) == 0 {
		return nil
	}

	u, err := url.ParseRequestURI(v)
	if err != nil {
		return err
	}
	*w = WebURL(*u)
	return nil
```

**File:** core/web/external_initiators_controller.go (L25-43)
```go
// ValidateExternalInitiator checks whether External Initiator parameters are
// safe for processing.
func ValidateExternalInitiator(
	ctx context.Context,
	exi *bridges.ExternalInitiatorRequest,
	orm bridges.ORM,
) error {
	fe := models.NewJSONAPIErrors()
	if len([]rune(exi.Name)) == 0 {
		fe.Add("No name specified")
	} else if !externalInitiatorNameRegexp.MatchString(exi.Name) {
		fe.Add("Name must be alphanumeric and may contain '_' or '-'")
	} else if _, err := orm.FindExternalInitiatorByName(ctx, exi.Name); err == nil {
		fe.Add(fmt.Sprintf("Name %v already exists", exi.Name))
	} else if !errors.Is(err, sql.ErrNoRows) {
		return errors.Wrap(err, "validating external initiator")
	}
	return fe.CoerceEmptyToNil()
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

**File:** core/web/external_initiators_controller.go (L62-96)
```go
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
```

**File:** core/web/router.go (L263-266)
```go
		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
```

**File:** core/config/toml/types.go (L2135-2150)
```go
func (w *WorkflowFetcherConfig) ValidateConfig() error {
	if w.URL == nil || *w.URL == "" {
		return nil // URL is optional
	}

	u, err := url.Parse(*w.URL)
	if err != nil {
		return configutils.ErrInvalid{Name: "URL", Value: *w.URL, Msg: "must be a valid URL"}
	}

	if u.Scheme != "file" && u.Scheme != "http" && u.Scheme != "https" {
		return configutils.ErrInvalid{Name: "URL", Value: *w.URL, Msg: "scheme must be one of: file, http, https"}
	}

	return nil
}
```
