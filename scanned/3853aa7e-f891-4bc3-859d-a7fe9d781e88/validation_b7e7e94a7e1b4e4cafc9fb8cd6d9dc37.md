Based on the investigation, no valid unprivileged-actor SSRF analog exists in this codebase for CVE-2016-3718.

Key findings supporting this conclusion:
- The `HTTPTask` in `core/services/pipeline/task.http.go` already implements SSRF protections: hardcoded URLs use an unrestricted client, but variable-interpolated URLs are routed through a restricted client by default that blocks local/private/multicast IP ranges (`clhttp.ErrDisallowedIP`), and bypassing this restriction requires an explicit `allowUnrestrictedNetworkAccess="true"` flag set by whoever authors the job spec. [1](#0-0) [2](#0-1) 
- Job/pipeline spec creation (where such URLs are defined) requires an authenticated session with the `run` role or higher — not an unprivileged actor. [3](#0-2) 
- `BridgeTask` URLs come from the node's own bridge registry, populated only through admin/edit-role-gated bridge creation endpoints (`authenticateUserCanEdit`), not user-supplied at run time.
<invoke name="codebase_search">
<parameter name="query">placeholder</parameter>
</invoke>

### Citations

**File:** core/services/pipeline/task.http.go (L70-74)
```go
		errors.Wrap(ResolveParam(&requestData, From(VarExpr(t.RequestData, vars), JSONWithVarExprs(t.RequestData, vars, false), nil)), "requestData"),
		// Any hardcoded strings used for URL uses the unrestricted HTTP adapter
		// Interpolated variable URLs use restricted HTTP adapter by default
		// You must set allowUnrestrictedNetworkAccess=true on the task to enable variable-interpolated URLs to make restricted network requests
		errors.Wrap(ResolveParam(&allowUnrestrictedNetworkAccess, From(NonemptyString(t.AllowUnrestrictedNetworkAccess), !variableRegexp.MatchString(t.URL))), "allowUnrestrictedNetworkAccess"),
```

**File:** core/services/pipeline/task.http.go (L106-113)
```go
	responseBytes, statusCode, respHeaders, start, finish, err := makeHTTPRequest(requestCtx, lggr, method, url, reqHeaders, requestData, client, t.config.DefaultHTTPLimit())
	elapsed := finish.Sub(start).Milliseconds()
	if err != nil {
		if errors.Is(errors.Cause(err), clhttp.ErrDisallowedIP) {
			err = errors.Wrap(err, `connections to local resources are disabled by default, if you are sure this is safe, you can enable on a per-task basis by setting allowUnrestrictedNetworkAccess="true" in the pipeline task spec, e.g. fetch [type="http" method=GET url="$(decode_cbor.url)" allowUnrestrictedNetworkAccess="true"]`)
		}
		return Result{Error: err}, RunInfo{IsRetryable: isRetryableHTTPError(statusCode, err)}
	}
```

**File:** core/web/pipeline_runs_controller.go (L109-126)
```go
	_, isUser := auth.GetAuthenticatedUser(c)
	_, isEI := auth.GetAuthenticatedExternalInitiator(c)
	// only users are allowed to run jobs using int IDs - EIs not allowed
	if isUser && !isEI {
		// Is it an int32? Then process it regardless of type
		var jobID int32
		jobID64, err := strconv.ParseInt(idStr, 10, 32)
		if err == nil {
			jobID = int32(jobID64)
			jobRunID, err := prc.App.RunJobV2(ctx, jobID, nil)
			if err != nil {
				jsonAPIError(c, http.StatusInternalServerError, err)
				return
			}
			respondWithPipelineRun(jobRunID)
			return
		}
	}
```
