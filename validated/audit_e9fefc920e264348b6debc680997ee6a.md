Audit Report

## Title
`AccessKey` and `OutgoingToken` credentials for External Initiators and Bridges are disclosed to unprivileged "view"-role authenticated users - (File: core/web/router.go)

## Summary
`GET /v2/external_initiators` and `GET /v2/bridge_types` (including `GET /v2/bridge_types/:BridgeName`) are registered without any `auth.RequiresEditRole`/`RequiresAdminRole` wrapper, while the corresponding create/update/delete endpoints for the same resources are gated behind `edit` role. As a result, a node user provisioned with only the lowest `view` role can read the `AccessKey` and `OutgoingToken` secrets for every configured External Initiator and Bridge, violating the intended privilege boundary between "can view configuration" and "can manage/create credentials."

## Finding Description
In the route table, `GET /v2/external_initiators`, `GET /v2/bridge_types`, and `GET /v2/bridge_types/:BridgeName` are wired with no role check, whereas `POST`/`PATCH`/`DELETE` on the same resources require `auth.RequiresEditRole`: [1](#0-0) 

The response presenters unconditionally serialize the secret fields:
- `ExternalInitiatorResource.AccessKey` / `.OutgoingToken`: [2](#0-1) 
- `BridgeResource.OutgoingToken` (only `IncomingToken` is create-only via `omitempty`): [3](#0-2) 

The node's own RBAC test suite documents this as intentionally reachable by `view` role (`viewOnlyAllowed: true`), the same role explicitly blocked from every mutating operation on these resources: [4](#0-3) 

The RBAC middleware itself demonstrates the intended boundary elsewhere: `view` and `run` roles are explicitly rejected from edit-gated handlers: [5](#0-4) 

**Important correction to the original claim's impact analysis:** External Initiator authentication (`AuthenticateExternalInitiator` / `AuthenticateByToken` flow) requires both the `AccessKey` *and* a `Secret`, verified via `HashedSecret`/`subtle.ConstantTimeCompare` against a per-initiator `Salt`: [6](#0-5) [7](#0-6)  The `Secret` is only ever returned once, at creation time, via the separate `ExternalInitiatorAuthentication` struct with `omitempty` tags, and is never included in `ExternalInitiatorResource`: [8](#0-7)  Therefore, leaking `AccessKey` alone via `GET /v2/external_initiators` is **not sufficient** to authenticate as or impersonate an External Initiator — the full impersonation chain claimed in the original report is not substantiated.

Similarly, for Bridges, `OutgoingToken` is distinct from `IncomingToken`; only `IncomingToken` (hashed via `incoming_token_hash`) is used by `AuthenticateBridgeType` to verify *incoming* requests to the node: [9](#0-8)  Inspection of `BridgeTask.Run`, the code path that makes outgoing HTTP calls to external adapters, shows it does not attach `OutgoingToken` as a request header — only job-spec-configured custom headers are sent: [10](#0-9)  This suggests `OutgoingToken` disclosure does not provide a demonstrated impersonation/forgery capability in this codebase; its downstream consumption (if any, e.g. by external adapter implementations expecting to validate it) could not be confirmed.

Despite the weaker-than-claimed impersonation impact, the core issue remains valid: these are secrets (`utils.NewSecret`-generated, high-entropy) intended to be creation-time-only or edit-role-gated, and they are nonetheless disclosed via unrestricted GET endpoints to the lowest-privileged authenticated role — an authorization/least-privilege violation matching CWE-200, analogous to the cited RhodeCode/Kallithea `get_repo` bug class of a normal read endpoint over-disclosing secrets.

## Impact Explanation
A user with only the `view` role — explicitly intended to have no ability to create, edit, or act on Bridges/External Initiators — can enumerate `AccessKey` and `OutgoingToken` values for all configured resources on the node via ordinary GET requests. This is a concrete secret-exfiltration/authorization-boundary violation (CWE-200), falling under the in-scope "key/secret exfiltration" impact category. However, based on code review, `AccessKey` alone does not enable full External Initiator impersonation (the paired `Secret` is required and is not exposed by these endpoints), and `OutgoingToken`'s verification/consumption path was not found to be wired into the outgoing bridge request flow in this codebase, so the severity should be treated as unauthorized secret disclosure rather than confirmed impersonation/forgery.

## Likelihood Explanation
High for the disclosure itself: it requires only a valid session with the lowest supported role, `view`, which is a standard, documented, and tested account type (`viewOnlyAllowed: true` in the RBAC test matrix). No race conditions, special configuration, or additional exploitation steps are needed to trigger the read.

## Recommendation
Remove `AccessKey`/`OutgoingToken` from `ExternalInitiatorResource` and `BridgeResource` (matching the existing `IncomingToken` `omitempty`/create-only pattern), or gate `GET /v2/external_initiators` and `GET /v2/bridge_types`(`/:BridgeName`) behind `auth.RequiresEditRole` to match the privilege level required to create/rotate these credentials.

## Proof of Concept
1. Create a node user with role `view` (`chainlink admin users create --role=view`).
2. Authenticate as that user and issue `GET /v2/external_initiators`; observe `accessKey` returned for every External Initiator per `ExternalInitiatorResource` (core/web/presenters/external_initiators.go:57-65).
3. Issue `GET /v2/bridge_types`; observe `outgoingToken` returned for every Bridge per `BridgeResource` (core/web/presenters/bridges.go:10-22).
4. Confirm via `core/web/auth/auth_test.go` lines 224-231 that both GET routes are `viewOnlyAllowed: true` while mutating routes on the same resources require `edit`.
5. To confirm the (limited) impact, attempt to use only the leaked `AccessKey` (without a valid `Secret`) against `AuthenticateExternalInitiator`/`AuthenticateByToken` — this should fail, demonstrating the disclosure does not by itself enable impersonation, but still represents unauthorized secret exposure to a lower-privileged role than intended.

### Citations

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

**File:** core/web/presenters/external_initiators.go (L12-20)
```go
// ExternalInitiatorAuthentication includes initiator and authentication details.
type ExternalInitiatorAuthentication struct {
	Name           string        `json:"name,omitempty"`
	URL            models.WebURL `json:"url"`
	AccessKey      string        `json:"incomingAccessKey,omitempty"`
	Secret         string        `json:"incomingSecret,omitempty"`
	OutgoingToken  string        `json:"outgoingToken,omitempty"`
	OutgoingSecret string        `json:"outgoingSecret,omitempty"`
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

**File:** core/web/auth/auth_test.go (L224-231)
```go
	{"GET", "/v2/external_initiators", true, true, true},
	{"POST", "/v2/external_initiators", false, false, true},
	{"DELETE", "/v2/external_initiators/MOCK", false, false, true},
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
	{"DELETE", "/v2/bridge_types/MOCK", false, false, true},
```

**File:** core/web/auth/auth.go (L119-141)
```go
func AuthenticateExternalInitiator(c *gin.Context, store Authenticator) error {
	ctx := c.Request.Context()
	eia := &auth.Token{
		AccessKey: c.GetHeader(static.ExternalInitiatorAccessKeyHeader),
		Secret:    c.GetHeader(static.ExternalInitiatorSecretHeader),
	}

	ei, err := store.FindExternalInitiator(ctx, eia)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return auth.ErrorAuthFailed
		}

		return errors.Wrap(err, "finding external initiator")
	}

	ok, err := bridges.AuthenticateExternalInitiator(eia, ei)
	if err != nil {
		return err
	}
	if !ok {
		return auth.ErrorAuthFailed
	}
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

**File:** core/bridges/external_initiator.go (L59-67)
```go
// AuthenticateExternalInitiator compares an auth against an initiator and
// returns true if the password hashes match
func AuthenticateExternalInitiator(eia *auth.Token, ea *ExternalInitiator) (bool, error) {
	hashedSecret, err := auth.HashedSecret(eia, ea.Salt)
	if err != nil {
		return false, err
	}
	return subtle.ConstantTimeCompare([]byte(hashedSecret), []byte(ea.HashedSecret)) == 1, nil
}
```

**File:** core/bridges/bridge_type.go (L104-112)
```go
// AuthenticateBridgeType returns true if the passed token matches its
// IncomingToken, or returns false with an error.
func AuthenticateBridgeType(bt *BridgeType, token string) (bool, error) {
	hash, err := incomingTokenHash(token, bt.Salt)
	if err != nil {
		return false, err
	}
	return subtle.ConstantTimeCompare([]byte(hash), []byte(bt.IncomingTokenHash)) == 1, nil
}
```

**File:** core/services/pipeline/task.bridge.go (L135-243)
```go
func (t *BridgeTask) Run(ctx context.Context, lggr logger.Logger, vars Vars, inputs []Result) (result Result, runInfo RunInfo) {
	inputValues, err := CheckInputs(inputs, -1, -1, 0)
	if err != nil {
		return Result{Error: errors.Wrap(err, "task inputs")}, runInfo
	}

	var (
		name              StringParam
		requestData       MapParam
		includeInputAtKey StringParam
		cacheTTL          Uint64Param
		reqHeaders        StringSliceParam
		checkRequired     BoolParam
	)
	err = stderrors.Join(
		errors.Wrap(ResolveParam(&name, From(NonemptyString(t.Name))), "name"),
		errors.Wrap(ResolveParam(&requestData, From(VarExpr(t.RequestData, vars), JSONWithVarExprs(t.RequestData, vars, false), nil)), "requestData"),
		errors.Wrap(ResolveParam(&includeInputAtKey, From(t.IncludeInputAtKey)), "includeInputAtKey"),
		errors.Wrap(ResolveParam(&cacheTTL, From(ValidDurationInSeconds(t.CacheTTL), t.bridgeConfig.BridgeCacheTTL().Seconds())), "cacheTTL"),
		errors.Wrap(ResolveParam(&reqHeaders, From(NonemptyString(t.Headers), "[]")), "reqHeaders"),
		errors.Wrap(ResolveParam(&checkRequired, From(NonemptyString(t.CheckRequired), false)), "checkRequired"),
	)
	if err != nil {
		return Result{Error: err}, runInfo
	}

	if len(reqHeaders)%2 != 0 {
		return Result{Error: errors.Errorf("headers must have an even number of elements")}, runInfo
	}

	overtimeCtx, cancel := overtimeContext(ctx)
	defer cancel()

	bridge, err := t.getBridgeFromName(overtimeCtx, name)
	if err != nil {
		return Result{Error: err}, runInfo
	}
	url := URLParam(bridge.URL)
	lookupPayload := make(MapParam)
	maps.Copy(lookupPayload, requestData)

	requestCtx, cancel := httpRequestCtx(ctx, t, t.config)
	defer cancel()
	if bridge.UseConnectionManager {
		bridgeConnManager := t.bridgeConnManager
		start := time.Now()
		responseBytes, obsErr := bridgeConnManager.GetObservation(bridge, map[string]any(lookupPayload))
		finish := time.Now()

		statusCode := http.StatusOK
		if obsErr != nil {
			statusCode = http.StatusGatewayTimeout
		}

		elapsed := finish.Sub(start)
		promBridgeLatency.WithLabelValues(t.Name, statusCodeGroup(statusCode)).Set(elapsed.Seconds())
		promBridgeLatencyHist.WithLabelValues(t.Name, statusCodeGroup(statusCode)).Observe(float64(elapsed.Milliseconds()))

		if telemetryCh := GetTelemetryCh(ctx); telemetryCh != nil {
			requestDataJSON, jsonErr := json.Marshal(lookupPayload)
			if jsonErr != nil {
				lggr.Warnw("Bridge task: failed to marshal request data for telemetry", "err", jsonErr)
			}
			bt := &BridgeTelemetry{
				Name:                   t.Name,
				RequestData:            requestDataJSON,
				ResponseData:           responseBytes,
				ResponseStatusCode:     statusCode,
				RequestStartTimestamp:  start,
				RequestFinishTimestamp: finish,
				SpecID:                 t.specID,
				DotID:                  t.DotID(),
			}
			if obsErr != nil {
				bt.ResponseError = new(string)
				*bt.ResponseError = obsErr.Error()
			}

			bt.resolveStreamID(t, vars, lggr)

			select {
			case telemetryCh <- bt:
			default:
				lggr.Warn("bridge task: telemetry channel is full, dropping telemetry")
			}
		}

		if obsErr != nil {
			lggr.Debugw("Bridge task: connection manager request failed",
				"response", string(responseBytes),
				"url", url.String(),
				"error", obsErr,
			)
			return Result{Error: obsErr}, RunInfo{IsRetryable: true}
		}
		return Result{Value: string(responseBytes)}, runInfo
	}

	requestDataJSON, err := t.finalizeAndMarshalBridgeRequestData(lggr, vars, inputValues, &requestData, includeInputAtKey)
	if err != nil {
		return Result{Error: err}, runInfo
	}
	logger.Sugared(lggr).Tracew("Bridge task: sending request",
		"requestData", string(requestDataJSON),
		"url", url.String(),
	)

	var cachedResponse bool
	responseBytes, statusCode, headers, start, finish, err := makeHTTPRequest(requestCtx, lggr, "POST", url, reqHeaders, requestData, t.httpClient, t.config.DefaultHTTPLimit())
```
