### Title
Path traversal in the workflow syncer HTTP fetcher allows escaping the configured base URL prefix - ([File: core/services/workflows/syncer/v2/fetcher.go])

### Summary
The workflow syncer's `newHTTPFetcher` fetches artifacts (workflow binaries/configs) by joining a configurable base URL with a caller-controlled relative path (`req.URL`), but unlike its sibling `newFileFetcher`, it never verifies that the resulting resource path stays within the intended base prefix, allowing directory traversal against the target HTTP host.

### Finding Description
`NewFetcherFunc` builds either a file-based or HTTP-based fetcher depending on the configured `baseURL` scheme [1](#0-0) .

`newFileFetcher` correctly guards against traversal: after joining the incoming `req.URL` with `basePath`, it explicitly checks `strings.HasPrefix(fullPath, basePath+string(filepath.Separator))` before reading the file, rejecting any path that escapes the base directory [2](#0-1) .

`newHTTPFetcher`, however, only calls `filepath.Clean` on `req.URL` and trims a leading `/`, then does `u.Path = filepath.Join(u.Path, cleanPath)` with no equivalent boundary check: [3](#0-2) 

`filepath.Clean` does not remove leading `..` segments when there is nothing left to cancel against (e.g. `Clean("../../secret")` stays `"../../secret"`), so `cleanPath` can still contain `..` components. `filepath.Join(u.Path, cleanPath)` then Cleans the combined path, and a value such as `../secret` can walk back past the configured base path segment (e.g. `u.Path = "/workflows/"` joined with `"../admin/config"` collapses to `/admin/config`), fetching a resource outside the directory that operators intended to expose via `baseURL`. This mirrors the CVE-2020-13449 root cause: a path built from an external caller's relative reference is joined to a base location without validating that the final resolved path remains under that base, permitting reads of files/resources the caller should not be able to reach.

The `fetcher_test.go` suite explicitly demonstrates that the equivalent file-fetcher rejects `../../../etc/passwd` with "is not within the basePath" [4](#0-3) , confirming the traversal-prevention pattern exists for one fetcher implementation but was not applied to the other.

### Impact Explanation
An attacker who controls the `req.URL` value used to invoke this fetcher (e.g., a workflow's registered binary/config URL, which is unprivileged-actor-supplied metadata processed by the node's workflow syncer) can craft a relative path with `../` sequences to make the node fetch content from unintended paths on the configured HTTP host — outside the directory the node operator intended to expose (e.g., another workflow owner's artifacts, or other resources hosted alongside the intended artifact prefix). This is a request/path scoping bypass that can lead to cross-user resource disclosure, matching the "cross-user response confusion" / unauthorized resource access impact category.

### Likelihood Explanation
I was unable to fully trace, within this session, the exact call site that supplies `req.URL` into `newHTTPFetcher` in production flow (e.g., whether it originates directly from on-chain workflow registry metadata such as `BinaryURL`/`ConfigURL`, which any address can register). The pattern strongly suggests `req.URL` is workflow/artifact-supplied and thus reachable from a low-privilege actor, but this specific data flow (registry → handler → fetcher `req.URL`) needs confirmation with full repository access, since the index used here did not surface the exact wiring code.

### Recommendation
Apply the same containment check used in `newFileFetcher` to `newHTTPFetcher`: after computing the joined `u.Path`, verify it still begins with the original base path prefix (or is exactly equal to it) before issuing the HTTP request, and reject the request otherwise.

### Proof of Concept
Given `baseURL = "https://artifacts.example.com/workflows/tenantA/"` and an attacker-controlled `req.URL = "../tenantB/secret-config.json"`:
1. `cleanPath := strings.TrimPrefix(filepath.Clean(req.URL), "/")` → `"../tenantB/secret-config.json"` (leading `..` preserved by `Clean`).
2. `u.Path = filepath.Join("/workflows/tenantA/", "../tenantB/secret-config.json")` → resolves to `/workflows/tenantB/secret-config.json`.
3. The node issues an HTTP GET to `https://artifacts.example.com/workflows/tenantB/secret-config.json`, fetching another tenant's artifact despite the fetcher being configured to only serve `tenantA`'s prefix — no equivalent `HasPrefix` check exists to stop this, unlike the file-based fetcher. [5](#0-4)

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

**File:** core/services/workflows/syncer/v2/fetcher_test.go (L443-448)
```go
		// Test path traversal attempt
		_, err = fetcher(ctx, "test-msg-id", ghcapabilities.Request{
			URL: "../../../etc/passwd",
		})
		require.Error(t, err)
		assert.Contains(t, err.Error(), "is not within the basePath")
```
