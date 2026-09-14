### Title
Path Traversal in Workflow Artifact HTTP Fetcher Escapes Configured Base Path - ([File: core/services/workflows/syncer/v2/fetcher.go])

### Summary
`newHTTPFetcher`, the HTTP implementation of `types.FetcherFunc` used to fetch workflow binaries/configs, joins an attacker-influenced request path onto an administrator-configured `baseURL` without verifying the resulting path remains within that base path's sub-directory. This mirrors the CVE-2023-5123 bug class: a subpath-scoped endpoint can be made to reach sibling/parent paths on the same host via `../` traversal.

### Finding Description
`NewFetcherFunc` builds either a file fetcher or an HTTP fetcher from an operator-configured `baseURL`. [1](#0-0) 

The file variant explicitly validates that the resolved path stays under `basePath` after joining: [2](#0-1) 

The HTTP variant (`newHTTPFetcher`) does not perform an equivalent containment check. It cleans the request path and joins it to the configured base URL's path, but `filepath.Join` collapses `..` segments together with the base path's own segments, so a `req.URL` such as `../admin/secret` can move the resulting request outside the intended sub-path of the same host/scheme: [3](#0-2) 

`req.URL` is attacker-influenced: it is populated from the `binaryURL`/`configURL` values associated with a workflow, which are supplied when a workflow is registered on-chain (an unprivileged workflow-owner action) and passed straight into the fetch request: [4](#0-3) [5](#0-4) 

This is the same root cause as the reported JSON-datasource-plugin CVE: a caller-supplied path parameter is concatenated onto an operator-configured base endpoint without validating that traversal characters can't push the resulting request outside the intended sub-path on that same host.

### Impact Explanation
If a node operator configures the HTTP artifact fetcher (`NewFetcherFunc` with an `http(s)://host/some/subpath` base URL) so that workflow binary/config artifacts are fetched from a restricted sub-path of an internal service, a workflow owner (an unprivileged, permissionless on-chain actor who can register workflows with arbitrary `binaryURL`/`configURL` values) can craft a URL value that, after traversal, causes the node to issue GET requests to other paths on that same host — potentially internal/administrative endpoints not meant to be reachable from workflow-controlled input. This is a server-side request path confusion / limited SSRF-adjacent issue reachable from an unprivileged, permissionless workflow registration.

### Likelihood Explanation
Requires the operator to actually be using `NewFetcherFunc`'s HTTP branch (this appears to be a local/dev/bypass-the-gateway configuration path per the code comment, rather than the default production gateway-mediated `FetcherService.Fetch`), and requires the configured base URL to have a security-relevant sub-path boundary. This narrows real-world exposure, but wherever this fetcher is enabled, the traversal is trivially triggerable by any account permitted to register a workflow (no special privilege).

### Recommendation
In `newHTTPFetcher`, after computing `u.Path = filepath.Join(u.Path, cleanPath)`, verify the resulting path is prefixed by the original base path (mirroring the check already done in `newFileFetcher`), and reject the request otherwise. Additionally consider rejecting any `req.URL` containing `..` segments before joining, rather than relying solely on `filepath.Clean`/`Join` semantics.

### Proof of Concept
1. Operator configures `NewFetcherFunc("http://internal-host/api/workflows", lggr)`, producing a `FetcherFunc` bound to `newHTTPFetcher`.
2. An unprivileged workflow owner registers a workflow with `binaryURL = "../admin/secret"` (or an equivalent value containing `../` segments in the path fed into `req.URL`).
3. `Store.FetchWorkflowArtifacts` passes this value straight through as `ghcapabilities.Request{URL: binaryURL, ...}`. [6](#0-5) 
4. Inside `newHTTPFetcher`, `cleanPath` becomes `../admin/secret`, and `filepath.Join("/api/workflows", "../admin/secret")` resolves to `/api/admin/secret` — outside the intended `/api/workflows` sub-path, on the same host configured by the operator. [7](#0-6) 

**Uncertainty:** I could not fully confirm where/whether `NewFetcherFunc`'s HTTP branch is wired into the production node's default configuration path (searches for the call site in `core/cmd/shell.go` returned only a match count without visible surrounding code, and the index may not contain the full file). The dominant, gateway-mediated artifact-fetch path (`FetcherService.Fetch`) does not have this issue since it delegates to `OutgoingConnectorHandler`/gateway allowlisting rather than direct URL-joining. If `NewFetcherFunc`'s HTTP variant is only used in local/test tooling and never in a production deployment with a security-relevant base path boundary, this finding's real-world impact is reduced to a defense-in-depth gap rather than an actively exploitable production vulnerability. Confirming exact production wiring would require starting a Devin session with full file access.

### Citations

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

**File:** core/services/workflows/syncer/v2/fetcher.go (L222-231)
```go
		fullPath := filepath.Clean(u.Path)

		// ensure that the incoming request URL is either relative or absolute but within the basePath
		if !filepath.IsAbs(fullPath) {
			// If it's not absolute, we assume it's relative to the basePath
			fullPath = filepath.Join(basePath, fullPath)
		}
		if !strings.HasPrefix(fullPath, basePath+string(filepath.Separator)) && fullPath != basePath {
			return nil, fmt.Errorf("request URL %s is not within the basePath %s", fullPath, basePath)
		}
```

**File:** core/services/workflows/syncer/v2/fetcher.go (L243-261)
```go
func newHTTPFetcher(baseURL string, lggr logger.Logger) types.FetcherFunc {
	client := &http.Client{
		Timeout: 30 * time.Second,
	}

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
```

**File:** core/services/workflows/artifacts/v2/store.go (L174-183)
```go
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

**File:** core/services/workflows/artifacts/v2/store.go (L216-227)
```go
		// Fetch the config files from the specified URLs.
		req := ghcapabilities.Request{
			URL:              configURL,
			Method:           http.MethodGet,
			MaxResponseBytes: safeUint32(uint64(maxResponseBytes)),
			WorkflowID:       workflowID,
		}

		config, err2 = h.fetchFn(ctx, messageID(configURL, workflowID), req)
		if err2 != nil {
			return nil, nil, &types.ArtifactFetchError{ArtifactType: "config", URL: configURL, Err: err2}
		}
```
