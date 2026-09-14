Found a concrete analog: `HTTPTask.Run` in `core/services/pipeline/task.http.go` logs `reqHeaders` verbatim at Debug level.

### Title
HTTP pipeline task logs raw request headers (including any secret/API keys placed in headers) at Debug level - (File: core/services/pipeline/task.http.go)

### Summary
The `http` pipeline adapter task logs the resolved `reqHeaders` slice unredacted whenever a job runs, mirroring the Ansible `uri` module CVE-2020-14330 bug class (secrets exposed through task/adapter logging).

### Finding Description
In `HTTPTask.Run`, after resolving the `Headers` param into `reqHeaders` (a flat `key1,value1,key2,value2,...` string slice), the code logs it directly: [1](#0-0) 
There is no redaction of header names/values (e.g. `Authorization`, `X-Api-Key`, etc.) before this `Debugw` call, unlike the web-server request logger which explicitly blacklists sensitive keys such as `password`: [2](#0-1) 
The bridge task (`task.bridge.go`) similarly logs `requestData` (the JSON body) at `Trace` level without redaction, though headers are passed separately and not logged there: [3](#0-2) 
`makeHTTPRequest` in `common_http.go` sets these headers on the outgoing request but performs no filtering; the earlier `Debugw` call in `task.http.go` is the only place headers are logged: [4](#0-3) 

### Impact Explanation
Job specs authored by node operators (or, in multi-tenant/Job-Distributor setups, users with job-creation privileges) commonly embed API keys/secrets directly as static header values in `http` task specs (e.g. `headers="[\"Authorization\", \"Bearer sk_live_...\"]"`). Anyone who can read node logs (e.g. via log aggregation, support tooling, or a lower-privileged operator with log access but not job-spec edit access) can recover these secrets. This is a data-confidentiality-only issue (matches the CVE's C:H/I:N/A:N profile) — no direct fund movement or auth bypass, but it is a real secret-disclosure vector reachable purely from an authorized job creator's job spec content ending up in operator-visible logs.

### Likelihood Explanation
Requires: (1) a job with an `http` task using static header-based credentials, and (2) `Debugw`-level logging enabled (default log level in Chainlink nodes is often `debug` in non-production/testing setups, and is user-configurable). This is a fairly common configuration for external-adapter-less HTTP fetch tasks, making this moderately likely to occur in practice.

### Recommendation
Redact header values (or at minimum, well-known sensitive header names like `Authorization`, `X-Api-Key`, `Api-Key`, `Cookie`) before logging `reqHeaders` in `task.http.go`, reusing/extending the existing `isBlacklisted`/`redact` pattern already used in `core/web/router.go`.

### Proof of Concept
1. Create a job with a pipeline task: `fetch [type="http" method=GET url="https://example.com" headers="[\"Authorization\", \"Bearer super-secret-key\"]"]`.
2. Run the node with `Log.Level = "debug"` (or trigger via any path that hits `Debugw`).
3. Execute the job run; observe node logs contain: `"HTTP task: sending request" ... "reqHeaders":["Authorization","Bearer super-secret-key"]`.
4. Anyone with read access to the node's log output (log aggregator, support engineer, etc.) can extract the secret.

**Note on uncertainty:** I could not fully verify default log level configuration across all deployment profiles, nor whether `VerboseLogging`/pipeline debug logging is disabled by default in production Helm charts — this affects real-world likelihood but not the existence of the code-level flaw. [1](#0-0)

### Citations

**File:** core/services/pipeline/task.http.go (L89-95)
```go
	lggr.Debugw("HTTP task: sending request",
		"requestData", string(requestDataJSON),
		"url", url.String(),
		"method", method,
		"reqHeaders", reqHeaders,
		"allowUnrestrictedNetworkAccess", allowUnrestrictedNetworkAccess,
	)
```

**File:** core/web/router.go (L643-658)
```go
// NOTE: keys must be in lowercase for case insensitive match
var blacklist = map[string]struct{}{
	"password":             {},
	"newpassword":          {},
	"oldpassword":          {},
	"current_password":     {},
	"new_account_password": {},
}

func isBlacklisted(k string) bool {
	lk := strings.ToLower(k)
	if _, ok := blacklist[lk]; ok || strings.Contains(lk, "password") {
		return true
	}
	return false
}
```

**File:** core/services/pipeline/task.bridge.go (L237-240)
```go
	logger.Sugared(lggr).Tracew("Bridge task: sending request",
		"requestData", string(requestDataJSON),
		"url", url.String(),
	)
```

**File:** core/services/pipeline/common_http.go (L44-50)
```go
	request.Header.Set("Content-Type", "application/json")
	if len(reqHeaders)%2 != 0 {
		panic("headers must have an even number of elements")
	}
	for i := 0; i+1 < len(reqHeaders); i += 2 {
		request.Header.Set(reqHeaders[i], reqHeaders[i+1])
	}
```
