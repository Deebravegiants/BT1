## Finding: Bridge/External Initiator URL fields accept `javascript:` scheme, no allowlist validation

### Title
Missing URL scheme validation on Bridge/ExternalInitiator `URL` field allows storage of `javascript:` URIs - (File: `core/store/models/common.go`)

### Summary
The `models.WebURL` type, used for both Bridge (`bridges.BridgeType`) and External Initiator (`bridges.ExternalInitiator`) URL fields, is parsed with `url.ParseRequestURI`, which only validates that the string is a syntactically well-formed absolute URI — it does not enforce an `http`/`https` scheme allowlist. This is the same bug class as CVE-2026-53472 (migration-planner `CredentialUrl` accepting `javascript:` URLs): a value with scheme `javascript:` parses successfully and is persisted and later served back through the REST/GraphQL APIs.

### Finding Description
`WebURL.UnmarshalJSON` and `WebURL.Scan` both call `url.ParseRequestURI`, with no scheme check: [1](#0-0) [2](#0-1) 

Both the Bridge and External Initiator "create" flows accept a raw URL from the request body and feed it through `url.ParseRequestURI` with no scheme restriction, then validate only that the URL string is non-empty: [3](#0-2) [4](#0-3) 

The GraphQL resolver path for creating/updating a bridge similarly parses the raw URL with `url.ParseRequestURI` and never checks the scheme: [5](#0-4) 

`ValidateExternalInitiator` (REST) only validates the `Name` field format and uniqueness — the `URL` is passed straight through unvalidated: [6](#0-5) 

Creation of bridges/external initiators requires only the `edit` role, while read access (`GET /v2/bridge_types`, `GET /v2/external_initiators`) is available to any authenticated role including the lower-privileged `view` role, with role checks enforced only on mutating routes: [7](#0-6) [8](#0-7) 

A `javascript:` URI is a syntactically valid absolute URI, so `url.ParseRequestURI("javascript:alert(1)")` succeeds and is stored verbatim, later returned via `presenters.NewBridgeResource`/`ExternalInitiatorResource` and the GraphQL `Bridge.url` field as plain strings.

### Impact Explanation
The stored value is served through both the REST JSON:API responses and the GraphQL `Bridge`/`ExternalInitiator` types as an unstructured string, consumed by the Operator UI. If any UI surface renders this field as an anchor/clickable link (common expectation for a "URL" field) rather than as a plain-text value, a lower-privileged `edit`-role user could plant a `javascript:` payload that executes in the browser session of a higher-privileged (`admin`) user who clicks or otherwise triggers rendering of the link — enabling session-scoped XSS, mirroring the CredentialUrl/Hybrid-Cloud-Console scenario in CVE-2026-53472.

### Likelihood Explanation
Likelihood is moderate: it requires (1) an authenticated actor with only the `edit` role (not admin) creating/updating a bridge or external initiator with a `javascript:` URL, which is fully permitted by current validation, and (2) an admin/higher-privileged user's browser rendering that URL as a clickable link in the Operator UI. The backend-side flaw (no scheme allowlist) is proven directly in this repository; the client-rendering half of the exploit chain lives in the (separate) Operator UI frontend, which is not part of this repository's index.

### Recommendation
Add scheme validation for `models.WebURL` (and the ad-hoc `url.ParseRequestURI` calls in `bridge_types_controller.go` and `resolver/mutation.go`) restricting accepted schemes to `http`/`https` only, similar to the pattern already used in `WorkflowFetcherConfig.ValidateConfig`: [9](#0-8) 
This should be enforced centrally (e.g., inside `WebURL.UnmarshalJSON`/`Scan`, or in `ValidateBridgeType`/`ValidateExternalInitiator`) so all entry points (REST, GraphQL, CLI) are covered.

### Proof of Concept
```
POST /v2/bridge_types
Authorization: <edit-role session/token>
Content-Type: application/json

{"name":"xss_bridge","url":"javascript:alert(document.cookie)"}
```
This request succeeds (HTTP 201) because `ValidateBridgeType` only checks the URL string is non-empty, and `url.ParseRequestURI` accepts the `javascript:` scheme. The stored URL is then returned unmodified to any authenticated caller via `GET /v2/bridge_types/xss_bridge` or the GraphQL `bridge(id: "xss_bridge") { url }` query.

### Citations

**File:** core/store/models/common.go (L118-135)
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
}
```

**File:** core/store/models/common.go (L153-166)
```go
// Scan reads the database value and returns an instance.
func (w *WebURL) Scan(value any) error {
	s, ok := value.(string)
	if !ok {
		return fmt.Errorf("unable to convert %v of %T to WebURL", value, value)
	}

	u, err := url.ParseRequestURI(s)
	if err != nil {
		return err
	}
	*w = WebURL(*u)
	return nil
}
```

**File:** core/web/bridge_types_controller.go (L36-53)
```go
func ValidateBridgeType(bt *bridges.BridgeTypeRequest) error {
	fe := models.NewJSONAPIErrors()
	if len(bt.Name.String()) < 1 {
		fe.Add("No name specified")
	}
	if _, err := bridges.ParseBridgeName(bt.Name.String()); err != nil {
		fe.Merge(err)
	}
	u := bt.URL.String()
	if len(strings.TrimSpace(u)) == 0 {
		fe.Add("URL must be present")
	}
	if bt.MinimumContractPayment != nil &&
		bt.MinimumContractPayment.Cmp(assets.NewLinkFromJuels(0)) < 0 {
		fe.Add("MinimumContractPayment must be positive")
	}
	return fe.CoerceEmptyToNil()
}
```

**File:** core/web/resolver/mutation.go (L62-87)
```go
// CreateBridge creates a new bridge.
func (r *Resolver) CreateBridge(ctx context.Context, args struct{ Input createBridgeInput }) (*CreateBridgePayloadResolver, error) {
	if err := authenticateUserCanEdit(ctx); err != nil {
		return nil, err
	}

	var webURL models.WebURL
	if len(args.Input.URL) != 0 {
		rURL, err := url.ParseRequestURI(args.Input.URL)
		if err != nil {
			return nil, err
		}
		webURL = models.WebURL(*rURL)
	}
	minContractPayment := &assets.Link{}
	if err := minContractPayment.UnmarshalText([]byte(args.Input.MinimumContractPayment)); err != nil {
		return nil, err
	}

	btr := &bridges.BridgeTypeRequest{
		Name:                   bridges.BridgeName(args.Input.Name),
		URL:                    webURL,
		Confirmations:          uint32(max(0, args.Input.Confirmations)),
		MinimumContractPayment: minContractPayment,
		UseConnectionManager:   args.Input.UseConnectionManager != nil && *args.Input.UseConnectionManager,
	}
```

**File:** core/web/resolver/mutation.go (L457-475)
```go
func (r *Resolver) UpdateBridge(ctx context.Context, args struct {
	ID    graphql.ID
	Input updateBridgeInput
}) (*UpdateBridgePayloadResolver, error) {
	if err := authenticateUserCanEdit(ctx); err != nil {
		return nil, err
	}

	var webURL models.WebURL
	if len(args.Input.URL) != 0 {
		rURL, err := url.ParseRequestURI(args.Input.URL)
		if err != nil {
			return nil, err
		}
		webURL = models.WebURL(*rURL)
	}
	minContractPayment := &assets.Link{}
	if err := minContractPayment.UnmarshalText([]byte(args.Input.MinimumContractPayment)); err != nil {
		return nil, err
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

**File:** core/web/router.go (L263-273)
```go
		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))

		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
```

**File:** core/web/auth/auth.go (L217-234)
```go
// RequiresEditRole extracts the user object from the context, and asserts the user's role is at least
// 'edit'
func RequiresEditRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView || user.Role == clsessions.UserRoleRun {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}
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
