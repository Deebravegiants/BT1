### Title
Local HTTP fetcher used to bypass the gateway follows redirects without SSRF protections - ([File: core/services/workflows/syncer/v2/fetcher.go])

### Summary
`newHTTPFetcher` in `core/services/workflows/syncer/v2/fetcher.go` builds a plain `*http.Client{Timeout: 30 * time.Second}` with no `CheckRedirect` override, so Go's default redirect-following behavior (up to 10 redirects across 301/302/303/307/308) applies. [1](#0-0)  This is the exact bug class in the Presto JDBC report: an HTTP client that transparently follows a 30x redirect issued by the remote server it is told to fetch from.

### Finding Description
Every other outbound HTTP client in this codebase that fetches attacker/workflow-influenced URLs explicitly disables redirects as a defense-in-depth SSRF control:
- The gateway's `network.httpClient` sets `SetCheckRedirect(disableRedirects)` on top of a `safeurl` allowlist (IP/port/scheme). [2](#0-1) [3](#0-2) 
- The `DirectHTTPAction` and `DirectConfidentialHTTPAction` capability fakes both explicitly set `CheckRedirect: disableRedirects` and are tested for this. [4](#0-3) [5](#0-4) 

In contrast, `newHTTPFetcher` — the fetcher used when the workflow syncer is configured with a local `file://` or `http(s)://` `baseURL` — is documented as bypassing the gateway entirely: "The implementation supports both file and HTTP(S) URLs and bypasses the gateway." [6](#0-5)  It constructs the request from `baseURL` joined with `req.URL` (the artifact path, e.g. derived from workflow binary/config URLs) and performs `client.Do(req2)` with no `CheckRedirect`, no IP/scheme allowlisting, and no response-body leak protection beyond a size limit. [7](#0-6) 

This fetcher is wired up via `NewFetcherFunc`, selected based on the scheme of a configured `baseURL` (`http`/`https` → `newHTTPFetcher`). [6](#0-5)  It is used by the workflow artifact `Store` as `fetchFn` to retrieve workflow binary/config artifacts named by URLs that ultimately originate from on-chain `WorkflowRegisteredEvent` data (`payload.BinaryURL`, `payload.ConfigURL`), i.e., workflow owner-supplied input, and passed through `FetchWorkflowArtifacts`. [8](#0-7) [9](#0-8) 

If this HTTP-scheme fetcher path is enabled (as opposed to the gateway-mediated `FetcherService.Fetch`), a malicious or compromised remote host that a workflow owner points `binaryURL`/`configURL` at could respond with a 30x redirect to an internal/private endpoint (metadata service, internal API, etc.), and the node would transparently follow it and ingest/log the resulting response as if it were the trusted artifact host.

### Impact Explanation
This enables SSRF from the node against its own internal network reachable from the workflow-syncer host: probing internal ports/services and reading internal HTTP responses that get treated as workflow binary/config content (persisted into `job.WorkflowSpec`) or surfaced through fetch error messages, which include the URL. Because every other HTTP egress path in the codebase treats "disable redirects" as a mandatory control, the omission here is inconsistent hardening rather than an accepted design choice.

### Likelihood Explanation
Exploitability depends on whether `newHTTPFetcher` (the `http`/`https` scheme path of `NewFetcherFunc`) is actually enabled in a given deployment instead of the gateway-mediated `FetcherService.Fetch`, which explicitly notes "redirects are currently not supported" and rejects non-2xx statuses without following them. [10](#0-9)  I could not confirm from the indexed code where/if `NewFetcherFunc` with an `http(s)://` base URL is instantiated in a production configuration path (only a reference exists in `core/cmd/shell.go`, which I was not able to inspect further within this session). This is a real, demonstrable gap in the client construction itself, but likelihood in production depends on deployment configuration that I could not fully verify with the available tools.

### Recommendation
Set `CheckRedirect` on the `http.Client` in `newHTTPFetcher` to reject redirects (mirroring `disableRedirects` used elsewhere), and/or route this fetch path through the same `safeurl`-based `network.httpClient` used by the gateway so IP/port/scheme allowlisting and redirect blocking apply uniformly to every artifact-fetch code path, regardless of whether it goes through the gateway.

### Proof of Concept
1. Configure the workflow syncer's fetcher with an `http://` base URL feeding `NewFetcherFunc`, so `newHTTPFetcher` is used for artifact retrieval instead of the gateway-mediated fetch.
2. Register/point a workflow's `binaryURL`/`configURL` (as consumed in `core/services/workflows/syncer/v2/handler.go` `createWorkflowSpec` → `FetchWorkflowArtifacts`) at an attacker-controlled HTTP server.
3. That server responds with `302 Location: http://169.254.169.254/latest/meta-data/` (or any internal address).
4. `newHTTPFetcher`'s `client.Do(req2)` transparently follows the redirect (no `CheckRedirect` set) and returns the internal response body as the "artifact," which gets base64-decoded/stored or surfaced in fetch error messages containing the fetched URL. [11](#0-10)

### Citations

**File:** core/services/workflows/syncer/v2/fetcher.go (L160-169)
```go
	if payload.ExecutionError {
		return nil, fmt.Errorf("execution error from gateway: %s", payload.ErrorMessage)
	}

	if payload.StatusCode < 200 || payload.StatusCode >= 300 {
		// NOTE: redirects are currently not supported
		return payload.Body, fmt.Errorf("request failed with status code: %d", payload.StatusCode)
	}

	return payload.Body, nil
```

**File:** core/services/workflows/syncer/v2/fetcher.go (L172-196)
```go
// NewFetcher creates a new FetcherFunc based on the provided URL configuration
// The implementation supports both file and HTTP(S) URLs and bypasses the gateway
func NewFetcherFunc(baseURL string, lggr logger.Logger) (types.FetcherFunc, error) {
	if baseURL == "" {
		return nil, errors.New("baseURL cannot be empty")
	}

	u, err := url.Parse(baseURL)
	if err != nil {
		return nil, fmt.Errorf("invalid URL: %w", err)
	}

	switch u.Scheme {
	case "file":
		// Ensure the basePath is absolute
		if !filepath.IsAbs(u.Path) {
			return nil, fmt.Errorf("basePath must be an absolute path, got: %s", u.Path)
		}
		return newFileFetcher(u.Path, lggr), nil
	case "http", "https":
		return newHTTPFetcher(baseURL, lggr), nil
	default:
		return nil, fmt.Errorf("unsupported URL scheme: %s", u.Scheme)
	}
}
```

**File:** core/services/workflows/syncer/v2/fetcher.go (L243-247)
```go
func newHTTPFetcher(baseURL string, lggr logger.Logger) types.FetcherFunc {
	client := &http.Client{
		Timeout: 30 * time.Second,
	}

```

**File:** core/services/workflows/syncer/v2/fetcher.go (L248-288)
```go
	return func(ctx context.Context, messageID string, req ghcapabilities.Request) ([]byte, error) {
		// Clean the path to prevent directory traversal
		cleanPath := strings.TrimPrefix(filepath.Clean(req.URL), "/")

		// Join base URL with path
		u, err := url.Parse(baseURL)
		if err != nil {
			return nil, fmt.Errorf("failed to parse base URL: %w", err)
		}

		u.Path = filepath.Join(u.Path, cleanPath)
		fetchURL := u.String()

		lggr.Debugw("Fetching HTTP resource", "url", fetchURL, "workflowID", req.WorkflowID)

		req2, err := http.NewRequestWithContext(ctx, http.MethodGet, fetchURL, nil)
		if err != nil {
			return nil, fmt.Errorf("failed to create request: %w", err)
		}

		resp, err := client.Do(req2)
		if err != nil {
			return nil, fmt.Errorf("HTTP request failed: %w", err)
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			return nil, fmt.Errorf("HTTP request failed with status code: %d", resp.StatusCode)
		}

		reader := resp.Body
		if req.MaxResponseBytes > 0 {
			reader = http.MaxBytesReader(nil, resp.Body, int64(req.MaxResponseBytes))
		}
		data, err := io.ReadAll(reader)
		if err != nil {
			return nil, fmt.Errorf("failed to read response body: %w", err)
		}

		return data, nil
	}
```

**File:** core/services/gateway/network/httpclient.go (L283-292)
```go
	safeConfigBuilder := safeurl.
		GetConfigBuilder().
		SetAllowedIPs(config.AllowedIPs...).
		SetAllowedIPsCIDR(config.AllowedIPsCIDR...).
		SetAllowedPorts(config.AllowedPorts...).
		SetAllowedSchemes(config.AllowedSchemes...).
		SetBlockedIPs(config.BlockedIPs...).
		SetBlockedIPsCIDR(config.BlockedIPsCIDR...).
		SetCheckRedirect(disableRedirects).
		SetTransport(defaultTransport)
```

**File:** core/services/gateway/network/httpclient.go (L354-360)
```go
func disableRedirects(req *http.Request, via []*http.Request) error {
	return &redirectsDisabledError{}
}

type redirectsDisabledError struct{}

func (e *redirectsDisabledError) Error() string { return "redirects are not allowed" }
```

**File:** core/capabilities/fakes/http_action.go (L196-203)
```go
// newHTTPClient builds the HTTP client used to make the outbound request. When
// the request carries mTLS auth, the client is configured to present the
// supplied certificate and private key as a client certificate.
func newHTTPClient(input *customhttp.Request, timeout time.Duration) (*http.Client, error) {
	client := &http.Client{
		Timeout:       timeout,
		CheckRedirect: disableRedirects,
	}
```

**File:** core/capabilities/fakes/confidential_http_action.go (L109-114)
```go
	// Create HTTP client with timeout (default 30 seconds)
	timeout := time.Duration(30) * time.Second
	client := &http.Client{
		Timeout:       timeout,
		CheckRedirect: disableRedirects,
	}
```

**File:** core/services/workflows/artifacts/v2/store.go (L163-184)
```go
	// Fetch the binary files from the specified URLs.
	var (
		binary, decodedBinary, config []byte
	)

	maxBinarySize, err := h.limiters.MaxBinarySize.Limit(ctx)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to get binary size limit: %w", err)
	} else if maxBinarySize < 0 {
		maxBinarySize = 0
	}
	req := ghcapabilities.Request{
		URL:              binaryURL,
		Method:           http.MethodGet,
		MaxResponseBytes: safeUint32(uint64(maxBinarySize)),
		WorkflowID:       workflowID,
	}
	binary, err = h.fetchFn(ctx, messageID(binaryURL, workflowID), req)
	if err != nil {
		return nil, nil, &types.ArtifactFetchError{ArtifactType: "binary", URL: binaryURL, Err: err}
	}

```

**File:** core/services/workflows/syncer/v2/handler.go (L797-801)
```go
	// With Workflow Registry contract v2 the BinaryURL and ConfigURL are expected to be identifiers that put through the Storage Service.
	decodedBinary, config, err := h.workflowArtifactsStore.FetchWorkflowArtifacts(ctx, wfID, payload.BinaryURL, payload.ConfigURL)
	if err != nil {
		return nil, err
	}
```
