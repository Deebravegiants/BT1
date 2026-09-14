Confirmed: `URLParam` (`core/services/pipeline/task_params.go:425-443`) is a thin wrapper around `net/url.URL` whose `String()` method calls `(*url.URL)(u).String()` directly — this is the standard library's `URL.String()`, which (unlike `URL.Redacted()`, used correctly elsewhere in this same repo for `Database.Backup.URL` at `core/services/periodicbackup/backup.go:178-186`) includes any userinfo/credentials embedded in the URL (e.g. `http://user:pass@host/path`) in cleartext.

This value is logged directly in the pipeline task runner:
- `core/services/pipeline/task.http.go:89-95` — `lggr.Debugw("HTTP task: sending request", "url", url.String(), ...)`
- `core/services/pipeline/task.http.go:115-120` — logged again on response
- `core/services/pipeline/task.bridge.go:237-240` and `:330-335` — `logger.Sugared(lggr).Tracew(... "url", url.String() ...)`
- `core/services/pipeline/task.bridge.go:425-452` (resolveFailureOrCache) — `lggr.Debugw("Bridge task: request failed", ..., "url", url.String(), ...)`

### Title
HTTP/Bridge pipeline task URLs with embedded credentials are logged in plaintext instead of being redacted - (File: core/services/pipeline/task_params.go)

### Summary
`URLParam.String()` at `core/services/pipeline/task_params.go:441-443` returns the full, unredacted URL (including any `user:password@` userinfo component), and this value is written directly into node logs by the `HTTPTask` and `BridgeTask` handlers whenever a job spec's `url` field or a bridge's registered adapter URL contains embedded basic-auth credentials.

### Finding Description
`net/url.URL` supports embedding `Userinfo` credentials directly in a URL string (`scheme://user:password@host/path`). The standard library provides `URL.String()` (includes credentials) and `URL.Redacted()` (masks the password as `xxxxx`). `URLParam` in `core/services/pipeline/task_params.go:425-443` only implements `String()`, calling `url.String()` directly with no redaction path at all.

This `URLParam` type is used by `HTTPTask.URL` and by `BridgeTask` (via `bridge.URL`), and its `.String()` output is passed straight into structured log calls:
- `core/services/pipeline/task.http.go:89-95` and `:115-120`
- `core/services/pipeline/task.bridge.go:237-240`, `:330-335`, and `:425-452`

Any job/workflow author who can define a pipeline spec (an `http` task with a hardcoded or interpolated URL, or a `bridge` task pointed at a bridge whose registered URL includes credentials) causes those credentials to be written to the node's log files/log stream in plaintext at Debug/Trace level — this is functionally identical to the Airflow bug class described in the report: credential-bearing URL/proxy fields treated as non-sensitive and passed to logging unmasked, while a redaction mechanism (`Redacted()`) exists elsewhere in the codebase (`core/services/periodicbackup/backup.go`) but is not applied here.

### Impact Explanation
If a bridge is configured with a URL containing embedded credentials (e.g., an external adapter requiring HTTP basic auth via userinfo, `http://apikey:secret@adapter.internal/path`), or a job spec's `http` task URL is set/interpolated to such a value, those credentials are written unmasked into the node's persistent logs on every task execution (Debug level for HTTP task, Trace/Debug level for bridge task, including failure/cache-fallback paths). Anyone with read access to log files, log aggregation systems, or log-shipping pipelines (which is a broader and less privileged audience than DB/API access) can recover the credentials, enabling unauthorized use of the external adapter or upstream service. This is a credential-disclosure vulnerability paralleling CVE-2025-68675.

### Likelihood Explanation
Likelihood is high in any deployment that (a) uses credential-embedded URLs for bridges/HTTP tasks — a supported and unremarkable configuration pattern for external adapters requiring basic auth, and (b) runs at Debug or Trace log level, which is common in non-trivial production Chainlink deployments for diagnosing pipeline issues, or is enabled temporarily during troubleshooting. No attacker interaction is required beyond configuring the job/bridge normally; the leak happens automatically on every run.

### Recommendation
Change `URLParam.String()` (and any other logging call sites that print `url.String()`) to use `url.Redacted()` semantics, or introduce a dedicated masked-string method for logging purposes and use it consistently in `task.http.go` and `task.bridge.go` log statements, mirroring the pattern already used for `Database.Backup.URL` in `core/services/periodicbackup/backup.go`.

### Proof of Concept
1. Create a bridge with URL `http://apikeyuser:supersecret@adapter.example.com/call` via `CreateBridgeType` (or configure an `http` pipeline task with `url="http://apikeyuser:supersecret@adapter.example.com/call"`).
2. Run a job that executes this bridge/HTTP task with node log level set to `debug` (or `trace` for bridge task, which is the default/typical operational level in troubleshooting).
3. Observe the node log output for the "HTTP task: sending request" / "Bridge task: sending request" (or failure/cache-fallback) log lines — the `url` field contains the full URL string `http://apikeyuser:supersecret@adapter.example.com/call`, exposing `apikeyuser:supersecret` in plaintext in the log store. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** core/services/pipeline/task_params.go (L425-443)
```go
type URLParam url.URL

func (u *URLParam) UnmarshalPipelineParam(val any) error {
	switch v := val.(type) {
	case string:
		theURL, err := url.ParseRequestURI(v)
		if err != nil {
			return errors.Wrap(ErrBadInput, err.Error())
		}
		*u = URLParam(*theURL)
		return nil
	default:
		return ErrBadInput
	}
}

func (u *URLParam) String() string {
	return (*url.URL)(u).String()
}
```

**File:** core/services/pipeline/task.http.go (L85-120)
```go
	requestDataJSON, err := json.Marshal(requestData)
	if err != nil {
		return Result{Error: err}, runInfo
	}
	lggr.Debugw("HTTP task: sending request",
		"requestData", string(requestDataJSON),
		"url", url.String(),
		"method", method,
		"reqHeaders", reqHeaders,
		"allowUnrestrictedNetworkAccess", allowUnrestrictedNetworkAccess,
	)

	requestCtx, cancel := httpRequestCtx(ctx, t, t.config)
	defer cancel()

	var client *http.Client
	if allowUnrestrictedNetworkAccess {
		client = t.unrestrictedHTTPClient
	} else {
		client = t.httpClient
	}
	responseBytes, statusCode, respHeaders, start, finish, err := makeHTTPRequest(requestCtx, lggr, method, url, reqHeaders, requestData, client, t.config.DefaultHTTPLimit())
	elapsed := finish.Sub(start).Milliseconds()
	if err != nil {
		if errors.Is(errors.Cause(err), clhttp.ErrDisallowedIP) {
			err = errors.Wrap(err, `connections to local resources are disabled by default, if you are sure this is safe, you can enable on a per-task basis by setting allowUnrestrictedNetworkAccess="true" in the pipeline task spec, e.g. fetch [type="http" method=GET url="$(decode_cbor.url)" allowUnrestrictedNetworkAccess="true"]`)
		}
		return Result{Error: err}, RunInfo{IsRetryable: isRetryableHTTPError(statusCode, err)}
	}

	lggr.Debugw("HTTP task got response",
		"response", string(responseBytes),
		"respHeaders", respHeaders,
		"url", url.String(),
		"dotID", t.DotID(),
	)
```

**File:** core/services/pipeline/task.bridge.go (L233-240)
```go
	requestDataJSON, err := t.finalizeAndMarshalBridgeRequestData(lggr, vars, inputValues, &requestData, includeInputAtKey)
	if err != nil {
		return Result{Error: err}, runInfo
	}
	logger.Sugared(lggr).Tracew("Bridge task: sending request",
		"requestData", string(requestDataJSON),
		"url", url.String(),
	)
```

**File:** core/services/pipeline/task.bridge.go (L325-336)
```go
	result = Result{Value: string(responseBytes)}

	promHTTPFetchTime.WithLabelValues(t.DotID()).Set(float64(elapsed))
	promHTTPResponseBodySize.WithLabelValues(t.DotID()).Set(float64(len(responseBytes)))

	logger.Sugared(lggr).Tracew("Bridge task: fetched answer",
		"answer", result.Value,
		"url", url.String(),
		"dotID", t.DotID(),
		"cached", cachedResponse,
	)
	return result, runInfo
```

**File:** core/services/pipeline/task.bridge.go (L420-452)
```go
		out.err = fmt.Errorf("bridge %s: failure status %d: %s", t.Name, out.statusCode, bestEffortExtractError(out.body))
	}

	promBridgeErrors.WithLabelValues(t.Name).Inc()
	if cacheTTL == 0 {
		lggr.Debugw("Bridge task: request failed",
			"response", string(out.body),
			"url", url.String(),
			"status_code", out.statusCode,
			"error", out.err,
		)
		retry := RunInfo{IsRetryable: isRetryableHTTPError(out.statusCode, out.err)}
		return out, &Result{Error: out.err}, &retry
	}

	//nolint:gosec // disable G115
	cachedBytes, cacheErr := t.orm.GetCachedResponse(ctx, t.dotID, t.specID, time.Duration(cacheTTL)*time.Second)
	if cacheErr != nil {
		promBridgeCacheErrors.WithLabelValues(t.Name).Inc()
		if !errors.Is(cacheErr, sql.ErrNoRows) {
			lggr.Warnw("Bridge task: cache fallback failed",
				"err", cacheErr.Error(),
				"url", url.String(),
			)
		}
		retry := RunInfo{IsRetryable: isRetryableHTTPError(out.statusCode, out.err)}
		return out, &Result{Error: out.err}, &retry
	}
	promBridgeCacheHits.WithLabelValues(t.Name).Inc()
	lggr.Debugw("Bridge task: request failed, falling back to cache",
		"response", string(cachedBytes),
		"url", url.String(),
	)
```

**File:** core/services/periodicbackup/backup.go (L178-186)
```go
	maskArgs := func(args []string) []string {
		masked := make([]string, len(args))
		copy(masked, args)
		masked[0] = backup.databaseURL.Redacted()
		return masked
	}

	maskedArgs := maskArgs(args)
	backup.logger.Debugf("Running pg_dump with: %v", maskedArgs)
```
