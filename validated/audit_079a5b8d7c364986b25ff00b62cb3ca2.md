### Title
Bridge/HTTP request URLs (including query-string secrets) are embedded in pipeline run error messages exposed to low-privileged Viewer users - ([File: core/services/pipeline/common_http.go])

### Summary
Chainlink node admins configure `bridges.BridgeType.URL` (or an `HTTPTask.URL`) as a plain, unredacted `models.WebURL`, not a `SecretURL`. External adapters conventionally embed API keys/tokens as query parameters in that URL. When the HTTP/bridge request to that endpoint fails (status ≥300), the request URL — including any embedded secret query parameters — is baked verbatim into the returned error string, which is then persisted as the pipeline run's error and exposed through the job-run read APIs to any authenticated user, including the lowest-privileged `view`-only role. This is directly analogous to CVE-2023-27587 (ReadToMyShoe), where an error message containing the full outbound request URL leaked an embedded API key to end users.

### Finding Description
`makeHTTPRequest` in `core/services/pipeline/common_http.go` builds the error text directly from the request URL when the response status is not 2xx: [1](#0-0) 
This function is invoked by `HTTPTask.Run` in `core/services/pipeline/task.http.go`, whose resulting error (still containing `url.String()`) is returned as `Result{Error: err}` for the pipeline run: [2](#0-1) 

`url` here is a node-operator-configured pipeline task parameter, and for bridge tasks the URL originates from `bridges.BridgeType.URL`, which is declared as a plain `models.WebURL` (not `models.SecretURL`/`config.SecretString`), i.e. it is not designed to be redacted: [3](#0-2) 
Compare this with fields that actually are protected from disclosure, such as `models.Secret`/`models.SecretURL`, which format/encode as `"xxxxx"`: [4](#0-3) 

Once the error is stored on the pipeline run (`AllErrors`/`FatalErrors`), it is served back through both the REST job-runs controller and the GraphQL `jobRun`/`jobRuns` resolvers: [5](#0-4) [6](#0-5) 

Access to these read paths only requires basic session authentication — `authenticateUser` merely checks that a session exists, and even the least privileged `sessions.UserRoleView` passes it (only `authenticateUserCanRun`/`CanEdit`/`IsAdmin` explicitly reject `UserRoleView`): [7](#0-6) 

So any node user with `view`-only access (who cannot create/edit bridges or run jobs) can read job-run error strings that leak the full bridge/HTTP-task URL — including any API key or token an admin embedded as a query parameter — for a bridge/job they did not configure.

By contrast, this codebase already recognizes this exact class of risk and has redaction utilities elsewhere: `core/web/router.go`'s `redact`/`readSanitizedJSON` blacklist-redact sensitive fields from logged request bodies, and `core/services/gateway/network/httpclient.go`'s `truncateLogError` explicitly strips path/query from `*url.Error` before logging, specifically to avoid leaking query-string secrets: [8](#0-7) 
No equivalent redaction is applied to the URL embedded in `makeHTTPRequest`'s user-facing error.

### Impact Explanation
If a node admin follows the common external-adapter pattern of putting an API key/token in a bridge or HTTP task URL's query string, any authenticated node user — even one restricted to the `view` role who cannot edit bridges, create jobs, or run jobs — can recover that secret simply by viewing job run history for jobs that use the affected bridge/HTTP task and triggering (or waiting for) a non-2xx response. This is a credential/secret-disclosure and privilege-boundary-crossing issue (low-privileged viewer obtains admin-configured external-adapter secrets), which could then be used to impersonate the node against the third-party API, incur cost, or exfiltrate data via the leaked key.

### Likelihood Explanation
Likelihood is moderate-to-high in typical deployments: query-string API keys are a common external-adapter integration pattern, non-2xx responses (auth failures, rate limits, adapter downtime) are routine occurrences, and job-run visibility to `view`-role users is a supported, intended feature of the node's RBAC model — no additional privilege escalation is needed beyond having a `view` account.

### Recommendation
- Redact query parameters (or the entire URL) from user/GraphQL/REST-facing error strings produced in `makeHTTPRequest` (`core/services/pipeline/common_http.go`), analogous to `truncateLogError` in the gateway's httpclient.
- Treat bridge/HTTP task URLs that may contain credentials as secrets (e.g., a `SecretURL`-like type) or explicitly strip query strings before interpolating them into any error surfaced to pipeline `Result.Error`.
- Apply the same sanitization within `task.bridge.go`'s error-construction path (`resolveFailureOrCache`) if any equivalent unredacted URL data flows into fatal/all error fields.

### Proof of Concept
1. As an admin, create a bridge/external adapter with `URL = "https://adapter.example.com/price?api_key=SECRETKEY123"`.
2. Create a job using an `HTTPTask`/bridge task pointing at that URL.
3. Cause (or wait for) the adapter to return a non-2xx status (e.g., temporary rate limiting, auth expiry, or adapter downtime).
4. `makeHTTPRequest` produces `err = "got error from https://adapter.example.com/price?api_key=SECRETKEY123: (status code 429) ..."`, which is stored as the run's error.
5. Log in as a `view`-role user (or any authenticated user) and call `GET /v2/jobs/:ID/runs` or the GraphQL `jobRun(id: ...) { allErrors fatalErrors }` query — the response includes the full URL with `api_key=SECRETKEY123`.

### Citations

**File:** core/services/pipeline/common_http.go (L71-76)
```go
	if statusCode >= 400 {
		err = errors.Errorf("got error from %s: (status code %v) %s", url.String(), statusCode, bestEffortExtractError(responseBytes))
	} else if statusCode >= 300 {
		err = errors.Errorf("redirect error %s: (status code %v) %s", url.String(), statusCode, bestEffortExtractError(responseBytes))
	}
	return responseBytes, statusCode, respHeaders, start, finish, err
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

**File:** core/bridges/bridge_type.go (L55-68)
```go
// BridgeType is used for external adapters and has fields for
// the name of the adapter and its URL.
type BridgeType struct {
	Name                   BridgeName    `db:"name"`
	URL                    models.WebURL `db:"url"`
	Confirmations          uint32        `db:"confirmations"`
	IncomingTokenHash      string        `db:"incoming_token_hash"`
	Salt                   string        `db:"salt"`
	OutgoingToken          string        `db:"outgoing_token"`
	MinimumContractPayment *assets.Link  `db:"minimum_contract_payment"`
	CreatedAt              time.Time     `db:"created_at"`
	UpdatedAt              time.Time     `db:"updated_at"`
	UseConnectionManager   bool          `db:"use_connection_manager" json:"useConnectionManager"`
}
```

**File:** core/store/models/secrets.go (L1-19)
```go
package models

import (
	"github.com/smartcontractkit/chainlink-common/pkg/config"
)

// Secret is a string that formats and encodes redacted, as "xxxxx".
// Deprecated
type Secret = config.SecretString

// Deprecated
func NewSecret(s string) *Secret { return config.NewSecretString(s) }

// SecretURL is a URL that formats and encodes redacted, as "xxxxx".
// Deprecated
type SecretURL = config.SecretURL

// Deprecated
func NewSecretURL(u *config.URL) *config.SecretURL { return (*config.SecretURL)(u) }
```

**File:** core/web/pipeline_runs_controller.go (L26-61)
```go
// Index returns all pipeline runs for a job.
// Example:
// "GET <application>/jobs/:ID/runs"
func (prc *PipelineRunsController) Index(c *gin.Context, size, page, offset int) {
	id := c.Param("ID")

	// Temporary: if no size is passed in, use a large page size. Remove once frontend can handle pagination
	if c.Query("size") == "" {
		size = 1000
	}

	var pipelineRuns []pipeline.Run
	var count int
	var err error

	ctx := c.Request.Context()
	if id == "" {
		pipelineRuns, count, err = prc.App.JobORM().PipelineRuns(ctx, nil, offset, size)
	} else {
		jobSpec := job.Job{}
		err = jobSpec.SetID(c.Param("ID"))
		if err != nil {
			jsonAPIError(c, http.StatusUnprocessableEntity, err)
			return
		}

		pipelineRuns, count, err = prc.App.JobORM().PipelineRuns(ctx, &jobSpec.ID, offset, size)
	}

	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	res := presenters.NewPipelineRunResources(pipelineRuns, prc.App.GetLogger())
	paginatedResponse(c, "pipelineRun", size, page, res, count, err)
```

**File:** core/web/resolver/job_run.go (L82-104)
```go
func (r *JobRunResolver) FatalErrors() []string {
	var errs []string

	for _, err := range r.run.StringFatalErrors() {
		if err != nil {
			errs = append(errs, *err)
		}
	}

	return errs
}

func (r *JobRunResolver) AllErrors() []string {
	var errs []string

	for _, err := range r.run.StringAllErrors() {
		if err != nil {
			errs = append(errs, *err)
		}
	}

	return errs
}
```

**File:** core/web/resolver/auth.go (L11-29)
```go
// Authenticates the user from the session cookie, presence of user inherently provides 'view' access.
func authenticateUser(ctx context.Context) error {
	if _, ok := auth.GetGQLAuthenticatedSession(ctx); !ok {
		return unauthorizedError{}
	}
	return nil
}

// Authenticates the user from the session cookie and asserts at least 'run' role.
func authenticateUserCanRun(ctx context.Context) error {
	session, ok := auth.GetGQLAuthenticatedSession(ctx)
	if !ok {
		return unauthorizedError{}
	}
	if session.User.Role == sessions.UserRoleView {
		return RoleNotPermittedError{session.User.Role}
	}
	return nil
}
```

**File:** core/services/gateway/network/httpclient.go (L362-374)
```go
func truncateLogError(err error) error {
	var urlErr *url.Error
	if !errors.As(err, &urlErr) {
		return err
	}
	u, parseErr := url.Parse(urlErr.URL)
	if parseErr != nil {
		return urlErr.Err
	}
	// trim to scheme + host only
	sanitized := &url.Error{Op: urlErr.Op, URL: u.Scheme + "://" + u.Host, Err: urlErr.Err}
	return sanitized
}
```
