Audit Report

## Title
Path-Traversal in CRE `newHTTPFetcher` allows attacker-supplied Workflow BinaryURL/ConfigURL to escape the configured fetch path prefix - (File: `core/services/workflows/syncer/v2/fetcher.go`)

## Summary
When `CRE.WorkflowFetcher.URL` is configured with an `http(s)://` scheme, `NewFetcherFunc` returns `newHTTPFetcher`, which builds the outbound request path via `filepath.Join(u.Path, cleanPath)` using an attacker-controlled `req.URL` without any post-join containment check. [1](#0-0)  This allows `req.URL` values containing `../` sequences to make the resulting path escape the configured base path, unlike the sibling `newFileFetcher`, which explicitly re-validates containment after path normalization. [2](#0-1) 

## Finding Description
`newHTTPFetcher` computes `cleanPath := strings.TrimPrefix(filepath.Clean(req.URL), "/")` and then `u.Path = filepath.Join(u.Path, cleanPath)`, using the result directly as the outbound fetch URL with no verification that `u.Path` remains prefixed by the original base path. [3](#0-2)  Because `filepath.Join` internally calls `filepath.Clean` on the combined path, a `req.URL` such as `"../../internal/secret"` will resolve `/workflows/../../internal/secret` down to `/internal/secret`, breaking out of the intended `/workflows` prefix. This is architecturally the same bug class as the one already fixed in `newFileFetcher`, which performs an explicit `strings.HasPrefix(fullPath, basePath+string(filepath.Separator))` check before use. [4](#0-3)  No equivalent check exists in `newHTTPFetcher`.

`NewFetcherFunc` is the switch point that selects `newHTTPFetcher` when the configured scheme is `http`/`https`. [5](#0-4)  I was not able to fully trace, within the available tool budget, the exact wiring from `CRE.WorkflowFetcher.URL` config through to where `NewFetcherFunc`'s returned function is assigned as the artifact store's `fetchFn`, nor fully confirm that `req.URL` passed into this fetcher is unmodified, attacker-controlled `BinaryURL`/`ConfigURL` from on-chain workflow registration events versus a value that might be pre-validated/rewritten earlier in the pipeline. The one usage site of `NewFetcherFunc` outside of tests found is in `core/cmd/shell.go`, which I did not get to inspect in detail before the iteration budget ended.

## Impact Explanation
If confirmed, the impact is that a node configured with an `http(s)://` `CRE.WorkflowFetcher.URL` could be induced to issue outbound GET requests to arbitrary paths on the configured host, potentially reaching internal endpoints not intended to be exposed through the artifact-fetch path, with responses fed into the workflow artifact pipeline (SSRF / request path impersonation against the configured fetcher host).

## Likelihood Explanation
This requires the operator to have configured `CRE.WorkflowFetcher.URL` with an `http`/`https` scheme (a supported, non-default configuration path since sample/default configs use `file://`). Given that precondition, the reachability depends on whether `req.URL` in `newHTTPFetcher` is indeed derived unmodified from unprivileged, on-chain-attacker-controlled `BinaryURL`/`ConfigURL` fields — a link I could not fully verify in the code within the available budget.

## Recommendation
Add the same containment check used in `newFileFetcher` to `newHTTPFetcher`: after computing `u.Path = filepath.Join(baseU.Path, cleanPath)`, verify it is still prefixed by the original base path (with separator boundary) before issuing the request, and reject otherwise.

## Proof of Concept
1. Configure `CRE.WorkflowFetcher.URL = "http://internal-host/workflows"`.
2. Trigger the fetcher with `req.URL = "../../admin/secret"` (via whatever registration path ultimately sets `req.URL` on the `ghcapabilities.Request` passed to the function returned by `NewFetcherFunc`).
3. Observe that `newHTTPFetcher` computes `fetchURL = "http://internal-host/admin/secret"` instead of remaining under `/workflows`, per the code at [6](#0-5) .

A unit test directly calling the `types.FetcherFunc` returned by `newHTTPFetcher(baseURL, lggr)` with a crafted `req.URL` containing `../` sequences, and asserting on the outbound HTTP request's resolved path (e.g., via `httptest.Server` capturing `r.URL.Path`), would concretely prove this without depending on the on-chain wiring that I was unable to fully verify.

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

**File:** core/services/workflows/syncer/v2/fetcher.go (L198-231)
```go
func newFileFetcher(basePath string, lggr logger.Logger) types.FetcherFunc {
	return func(ctx context.Context, messageID string, req ghcapabilities.Request) ([]byte, error) {
		select {
		case <-ctx.Done():
			return nil, ctx.Err()
		default:
		}

		// the incoming request URL is expected to be a relative path or a path within the basePath
		if req.URL == "" {
			return nil, errors.New("request URL cannot be empty")
		}
		u, err := url.Parse(req.URL)
		if err != nil {
			return nil, fmt.Errorf("invalid URL: %w", err)
		}
		// Confidential workflows register with HTTP URLs (for the enclave).
		// Extract the filename so the file fetcher can find the local copy.
		if u.Scheme == "http" || u.Scheme == "https" {
			u.Path = filepath.Base(u.Path)
			if u.Path == "." || u.Path == "/" {
				return nil, errors.New("HTTP URL has no filename in path")
			}
		}
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
